from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.categorias.models import Categoria


class Movimiento(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="movimientos",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name="movimiento_monto_positivo",
            ),
        ]
        ordering = ["-fecha", "-creado_en"]

    def clean(self):
        if (
            self.categoria_id
            and self.usuario_id
            and self.categoria.usuario_id != self.usuario_id
        ):
            raise ValidationError(
                {"categoria": "La categoría debe pertenecer al usuario del movimiento."}
            )

    def __str__(self):
        return f"{self.fecha} - {self.categoria.nombre} - {self.monto}"
