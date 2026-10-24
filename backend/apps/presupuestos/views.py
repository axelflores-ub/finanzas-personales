from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Presupuesto
from .serializers import PresupuestoSerializer


class PresupuestoViewSet(viewsets.ModelViewSet):
    serializer_class = PresupuestoSerializer

    def get_queryset(self):
        queryset = Presupuesto.objects.filter(usuario=self.request.user).select_related(
            "categoria"
        )
        params = self.request.query_params

        mes = params.get("mes")
        if mes:
            if not mes.isdigit() or not (1 <= int(mes) <= 12):
                raise ValidationError({"mes": "mes debe ser un entero entre 1 y 12."})
            queryset = queryset.filter(mes=int(mes))

        anio = params.get("anio")
        if anio:
            if not anio.isdigit():
                raise ValidationError({"anio": "anio debe ser un número entero."})
            queryset = queryset.filter(anio=int(anio))

        return queryset
