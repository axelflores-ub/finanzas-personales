from django.contrib import admin

from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "usuario", "creado_en")
    list_filter = ("tipo", "usuario")
    search_fields = ("nombre",)
    ordering = ("usuario", "nombre")
