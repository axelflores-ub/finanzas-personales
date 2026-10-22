from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/resumen/", views.resumen, name="dashboard-resumen"),
    path(
        "dashboard/gastos-por-categoria/",
        views.gastos_por_categoria,
        name="dashboard-gastos-por-categoria",
    ),
]
