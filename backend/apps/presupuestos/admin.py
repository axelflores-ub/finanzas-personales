from django.contrib import admin

from .models import Presupuesto


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ("categoria", "mes", "anio", "monto_limite", "usuario")
    list_filter = ("anio", "mes", "usuario")
    search_fields = ("categoria__nombre",)
    ordering = ("-anio", "-mes")
