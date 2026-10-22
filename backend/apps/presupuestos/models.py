from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.categorias.models import Categoria


class Presupuesto(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="presupuestos",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="presupuestos",
    )
    mes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    anio = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000)])
    monto_limite = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "categoria", "mes", "anio"],
                name="presupuesto_unico_por_categoria_periodo",
            ),
            models.CheckConstraint(
                condition=models.Q(monto_limite__gt=0),
                name="presupuesto_monto_positivo",
            ),
            models.CheckConstraint(
                condition=models.Q(mes__gte=1) & models.Q(mes__lte=12),
                name="presupuesto_mes_valido",
            ),
        ]
        ordering = ["-anio", "-mes"]

    def clean(self):
        errors = {}
        if (
            self.categoria_id
            and self.usuario_id
            and self.categoria.usuario_id != self.usuario_id
        ):
            errors["categoria"] = "La categoría debe pertenecer al usuario del presupuesto."
        elif self.categoria_id and self.categoria.tipo != Categoria.Tipo.GASTO:
            errors["categoria"] = (
                "El presupuesto solo puede asociarse a categorías de tipo GASTO."
            )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.categoria.nombre} {self.mes}/{self.anio}"
