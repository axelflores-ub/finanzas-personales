from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento

from .models import Presupuesto

CERO = Decimal("0.00")
DOS_DECIMALES = Decimal("0.01")


class PresupuestoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    gasto_real = serializers.SerializerMethodField()
    porcentaje_utilizado = serializers.SerializerMethodField()
    restante = serializers.SerializerMethodField()

    class Meta:
        model = Presupuesto
        fields = [
            "id",
            "categoria",
            "categoria_nombre",
            "mes",
            "anio",
            "monto_limite",
            "gasto_real",
            "porcentaje_utilizado",
            "restante",
            "creado_en",
        ]
        read_only_fields = ["id", "creado_en"]

    def _gasto_real(self, obj):
        # Se calcula en vivo con Sum/Decimal, nunca se guarda en la base.
        # Se cachea en la instancia porque los 3 SerializerMethodField de
        # abajo lo necesitan y si no, se repetiría la query 3 veces por fila.
        if not hasattr(obj, "_gasto_real_cache"):
            total = Movimiento.objects.filter(
                usuario_id=obj.usuario_id,
                categoria_id=obj.categoria_id,
                fecha__year=obj.anio,
                fecha__month=obj.mes,
            ).aggregate(total=Sum("monto"))["total"]
            obj._gasto_real_cache = total or CERO
        return obj._gasto_real_cache

    def get_gasto_real(self, obj):
        return str(self._gasto_real(obj).quantize(DOS_DECIMALES))

    def get_porcentaje_utilizado(self, obj):
        gasto = self._gasto_real(obj)
        porcentaje = (gasto / obj.monto_limite * 100) if obj.monto_limite else CERO
        return str(porcentaje.quantize(DOS_DECIMALES))

    def get_restante(self, obj):
        gasto = self._gasto_real(obj)
        return str((obj.monto_limite - gasto).quantize(DOS_DECIMALES))

    def validate(self, attrs):
        usuario = self.context["request"].user
        categoria = attrs.get("categoria", getattr(self.instance, "categoria", None))
        mes = attrs.get("mes", getattr(self.instance, "mes", None))
        anio = attrs.get("anio", getattr(self.instance, "anio", None))

        if categoria is not None and categoria.usuario_id != usuario.id:
            raise serializers.ValidationError(
                {"categoria": "La categoría debe pertenecer al usuario autenticado."}
            )
        if categoria is not None and categoria.tipo != Categoria.Tipo.GASTO:
            raise serializers.ValidationError(
                {"categoria": "El presupuesto solo puede asociarse a categorías de tipo GASTO."}
            )

        queryset = Presupuesto.objects.filter(
            usuario=usuario, categoria=categoria, mes=mes, anio=anio
        )
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                {"mes": "Ya existe un presupuesto para esa categoría en ese período."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)
