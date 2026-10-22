from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from apps.categorias.models import Categoria

from .models import Movimiento
from .serializers import MovimientoSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoSerializer

    def get_queryset(self):
        queryset = Movimiento.objects.filter(usuario=self.request.user).select_related(
            "categoria"
        )
        params = self.request.query_params

        fecha_desde = self._parse_fecha(params.get("fecha_desde"), "fecha_desde")
        fecha_hasta = self._parse_fecha(params.get("fecha_hasta"), "fecha_hasta")

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise ValidationError(
                {"fecha_desde": "fecha_desde no puede ser posterior a fecha_hasta."}
            )
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        tipo = params.get("tipo")
        if tipo:
            if tipo not in Categoria.Tipo.values:
                raise ValidationError(
                    {
                        "tipo": (
                            "Tipo inválido. Valores permitidos: "
                            f"{', '.join(Categoria.Tipo.values)}."
                        )
                    }
                )
            queryset = queryset.filter(categoria__tipo=tipo)

        categoria_id = params.get("categoria")
        if categoria_id:
            if not categoria_id.isdigit():
                raise ValidationError({"categoria": "El id de categoría debe ser numérico."})
            queryset = queryset.filter(categoria_id=categoria_id)

        return queryset

    @staticmethod
    def _parse_fecha(value, field_name):
        if not value:
            return None
        try:
            parsed = parse_date(value)
        except ValueError:
            parsed = None
        if parsed is None:
            raise ValidationError({field_name: "Fecha inválida. Formato esperado: YYYY-MM-DD."})
        return parsed
