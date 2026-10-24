from decimal import Decimal

from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento
from apps.presupuestos.models import Presupuesto

from .validators import parse_anio, parse_periodo

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


@api_view(["GET"])
def presupuestos_resumen(request):
    """Presupuesto total, gasto real presupuestado y % utilizado del período.

    Contrato JSON documentado en README.md (seccion Dashboard). Separado de
    `resumen`: acá "gasto_real" solo suma categorías con presupuesto en el
    período (no el gasto general), y cada categoría presupuestada aporta una
    sola vez porque el modelo Presupuesto es único por (usuario, categoria,
    mes, anio).
    """
    mes, anio = parse_periodo(request.query_params)

    presupuestos = Presupuesto.objects.filter(usuario=request.user, mes=mes, anio=anio)
    presupuesto_total = presupuestos.aggregate(total=Sum("monto_limite"))["total"] or CERO

    categoria_ids = presupuestos.values_list("categoria_id", flat=True)
    gasto_real_presupuestado = (
        Movimiento.objects.filter(
            usuario=request.user,
            categoria_id__in=categoria_ids,
            fecha__year=anio,
            fecha__month=mes,
        ).aggregate(total=Sum("monto"))["total"]
        or CERO
    )

    porcentaje = (
        (gasto_real_presupuestado / presupuesto_total * 100) if presupuesto_total > 0 else CERO
    )

    return Response(
        {
            "mes": mes,
            "anio": anio,
            "presupuesto_total": str(presupuesto_total.quantize(DOS_DECIMALES)),
            "gasto_real_presupuestado": str(gasto_real_presupuestado.quantize(DOS_DECIMALES)),
            "porcentaje_utilizado": str(porcentaje.quantize(DOS_DECIMALES)),
        }
    )


@api_view(["GET"])
def evolucion_mensual(request):
    """Ingresos, gastos y balance mes a mes (1-12) del usuario para un año.

    Contrato JSON documentado en README.md (seccion Dashboard). Siempre
    devuelve los 12 meses, con ceros en los que no tienen movimientos.
    """
    anio = parse_anio(request.query_params)

    agregados = (
        Movimiento.objects.filter(usuario=request.user, fecha__year=anio)
        .values("fecha__month", "categoria__tipo")
        .annotate(total=Sum("monto"))
    )

    ingresos_por_mes = {mes: CERO for mes in range(1, 13)}
    gastos_por_mes = {mes: CERO for mes in range(1, 13)}
    for item in agregados:
        destino = (
            ingresos_por_mes
            if item["categoria__tipo"] == Categoria.Tipo.INGRESO
            else gastos_por_mes
        )
        destino[item["fecha__month"]] = item["total"]

    meses = []
    for mes in range(1, 13):
        ingresos = ingresos_por_mes[mes]
        gastos = gastos_por_mes[mes]
        balance = ingresos - gastos
        meses.append(
            {
                "mes": mes,
                "ingresos": str(ingresos.quantize(DOS_DECIMALES)),
                "gastos": str(gastos.quantize(DOS_DECIMALES)),
                "balance": str(balance.quantize(DOS_DECIMALES)),
            }
        )

    return Response({"anio": anio, "meses": meses})
