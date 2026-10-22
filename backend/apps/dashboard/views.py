from decimal import Decimal

from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento

from .validators import parse_periodo

CERO = Decimal("0.00")
DOS_DECIMALES = Decimal("0.01")


@api_view(["GET"])
def resumen(request):
    """Totales de ingresos, gastos y balance del usuario para un período.

    Contrato JSON documentado en README.md (seccion Dashboard).
    """
    mes, anio = parse_periodo(request.query_params)

    movimientos = Movimiento.objects.filter(usuario=request.user, fecha__year=anio, fecha__month=mes)

    ingresos = (
        movimientos.filter(categoria__tipo=Categoria.Tipo.INGRESO).aggregate(total=Sum("monto"))[
            "total"
        ]
        or CERO
    )
    gastos = (
        movimientos.filter(categoria__tipo=Categoria.Tipo.GASTO).aggregate(total=Sum("monto"))[
            "total"
        ]
        or CERO
    )
    balance = ingresos - gastos

    return Response(
        {
            "mes": mes,
            "anio": anio,
            "ingresos": str(ingresos.quantize(DOS_DECIMALES)),
            "gastos": str(gastos.quantize(DOS_DECIMALES)),
            "balance": str(balance.quantize(DOS_DECIMALES)),
        }
    )


@api_view(["GET"])
def gastos_por_categoria(request):
    """Gasto total y porcentaje por categoría del usuario para un período.

    Contrato JSON documentado en README.md (seccion Dashboard).
    """
    mes, anio = parse_periodo(request.query_params)

    gastos_qs = (
        Movimiento.objects.filter(
            usuario=request.user,
            categoria__tipo=Categoria.Tipo.GASTO,
            fecha__year=anio,
            fecha__month=mes,
        )
        .values("categoria_id", "categoria__nombre")
        .annotate(total=Sum("monto"))
        .order_by("-total")
    )

    total_gastos = sum((item["total"] for item in gastos_qs), CERO)

    categorias = []
    for item in gastos_qs:
        monto = item["total"]
        porcentaje = (monto / total_gastos * 100) if total_gastos > 0 else CERO
        categorias.append(
            {
                "categoria_id": item["categoria_id"],
                "categoria_nombre": item["categoria__nombre"],
                "monto": str(monto.quantize(DOS_DECIMALES)),
                "porcentaje": str(porcentaje.quantize(DOS_DECIMALES)),
            }
        )

    return Response(
        {
            "mes": mes,
            "anio": anio,
            "total_gastos": str(total_gastos.quantize(DOS_DECIMALES)),
            "categorias": categorias,
        }
    )
