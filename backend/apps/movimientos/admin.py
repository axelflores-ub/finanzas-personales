from django.contrib import admin

from .models import Movimiento


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "categoria", "monto", "usuario")
    list_filter = ("categoria__tipo", "usuario", "categoria")
    search_fields = ("descripcion",)
    date_hierarchy = "fecha"
    ordering = ("-fecha",)
