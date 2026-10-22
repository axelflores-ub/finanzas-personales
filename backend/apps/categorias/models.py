from django.conf import settings
from django.db import models


class Categoria(models.Model):
    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        GASTO = "GASTO", "Gasto"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categorias",
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nombre", "tipo"],
                name="categoria_unica_por_usuario_nombre_tipo",
            ),
        ]
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
