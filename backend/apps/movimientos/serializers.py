from rest_framework import serializers

from .models import Movimiento


class MovimientoSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="categoria.tipo", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            "id",
            "categoria",
            "categoria_nombre",
            "tipo",
            "monto",
            "fecha",
            "descripcion",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def validate_categoria(self, categoria):
        usuario = self.context["request"].user
        if categoria.usuario_id != usuario.id:
            raise serializers.ValidationError(
                "La categoría debe pertenecer al usuario autenticado."
            )
        return categoria

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)
