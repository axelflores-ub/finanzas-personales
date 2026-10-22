from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento

RESUMEN_URL = "/api/dashboard/resumen/"
GASTOS_POR_CATEGORIA_URL = "/api/dashboard/gastos-por-categoria/"


class DashboardApiAuthTests(APITestCase):
    def test_resumen_sin_autenticacion_devuelve_401(self):
        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_gastos_por_categoria_sin_autenticacion_devuelve_401(self):
        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": 10, "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardResumenTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.otro_usuario = get_user_model().objects.create_user(username="beto", password="x")
        self.client.force_authenticate(user=self.user)

        self.cat_sueldo = Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        self.cat_alimentacion = Categoria.objects.create(
            usuario=self.user, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )

    # 1. Totales de ingresos y gastos. / 2. Balance.
    def test_totales_y_balance(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("150000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("30000.00"),
            fecha="2026-10-10",
        )

        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ingresos"], "150000.00")
        self.assertEqual(response.data["gastos"], "30000.00")
        self.assertEqual(response.data["balance"], "120000.00")

    # 3. Balance negativo.
    def test_balance_negativo(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("5000.00"),
            fecha="2026-10-10",
        )

        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.data["balance"], "-4000.00")

    # 4. Filtrado por mes y año.
    def test_filtra_por_mes_y_anio(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("2000.00"),
            fecha="2026-11-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("3000.00"),
            fecha="2025-10-05",
        )

        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.data["ingresos"], "1000.00")

    # 5. Aislamiento de datos entre usuarios.
    def test_no_incluye_movimientos_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=categoria_ajena, monto=Decimal("999999.00"),
            fecha="2026-10-05",
        )

        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.data["ingresos"], "0.00")
        self.assertEqual(response.data["gastos"], "0.00")
        self.assertEqual(response.data["balance"], "0.00")

    # 6. Respuestas sin movimientos.
    def test_sin_movimientos_devuelve_ceros(self):
        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ingresos"], "0.00")
        self.assertEqual(response.data["gastos"], "0.00")
        self.assertEqual(response.data["balance"], "0.00")

    # 9. Parámetros inválidos.
    def test_mes_faltante_devuelve_400(self):
        response = self.client.get(RESUMEN_URL, {"anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mes", response.data)

    def test_mes_fuera_de_rango_devuelve_400(self):
        response = self.client.get(RESUMEN_URL, {"mes": 13, "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mes", response.data)

    def test_mes_no_numerico_devuelve_400(self):
        response = self.client.get(RESUMEN_URL, {"mes": "octubre", "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mes", response.data)

    def test_anio_faltante_devuelve_400(self):
        response = self.client.get(RESUMEN_URL, {"mes": 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("anio", response.data)

    def test_anio_fuera_de_rango_devuelve_400(self):
        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 1800})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("anio", response.data)

    # 11. Precisión de importes con decimales.
    def test_precision_decimal(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.10"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.20"),
            fecha="2026-10-06",
        )

        response = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.data["ingresos"], "2000.30")


class DashboardGastosPorCategoriaTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.client.force_authenticate(user=self.user)

        self.cat_alimentacion = Categoria.objects.create(
            usuario=self.user, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        self.cat_transporte = Categoria.objects.create(
            usuario=self.user, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )
        self.cat_sueldo = Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )

    # 7. Porcentajes por categoría.
    def test_porcentajes_por_categoria(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("7500.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_transporte, monto=Decimal("2500.00"),
            fecha="2026-10-10",
        )

        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_gastos"], "10000.00")

        por_nombre = {c["categoria_nombre"]: c for c in response.data["categorias"]}
        self.assertEqual(por_nombre["Alimentación"]["monto"], "7500.00")
        self.assertEqual(por_nombre["Alimentación"]["porcentaje"], "75.00")
        self.assertEqual(por_nombre["Transporte"]["monto"], "2500.00")
        self.assertEqual(por_nombre["Transporte"]["porcentaje"], "25.00")

    # 8. Categorías sin gastos excluidas.
    def test_categoria_sin_gastos_no_aparece(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("1000.00"),
            fecha="2026-10-05",
        )

        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": 10, "anio": 2026})

        nombres = [c["categoria_nombre"] for c in response.data["categorias"]]
        self.assertNotIn("Transporte", nombres)

    def test_categoria_de_ingreso_no_aparece(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("1000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("50000.00"),
            fecha="2026-10-05",
        )

        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": 10, "anio": 2026})

        nombres = [c["categoria_nombre"] for c in response.data["categorias"]]
        self.assertNotIn("Sueldo", nombres)

    def test_sin_gastos_devuelve_lista_vacia(self):
        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["categorias"], [])
        self.assertEqual(response.data["total_gastos"], "0.00")

    def test_parametros_invalidos_devuelve_400(self):
        response = self.client.get(GASTOS_POR_CATEGORIA_URL, {"mes": "x", "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
