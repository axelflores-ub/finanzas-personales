from rest_framework import serializers

from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "tipo", "creado_en"]
        read_only_fields = ["id", "creado_en"]

    def validate(self, attrs):
        usuario = self.context["request"].user
        nombre = attrs.get("nombre", getattr(self.instance, "nombre", None))
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))

        queryset = Categoria.objects.filter(usuario=usuario, nombre=nombre, tipo=tipo)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                {"nombre": "Ya existe una categoría con ese nombre y tipo."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)
