from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento
from apps.presupuestos.models import Presupuesto

RESUMEN_URL = "/api/dashboard/resumen/"
GASTOS_POR_CATEGORIA_URL = "/api/dashboard/gastos-por-categoria/"
PRESUPUESTOS_RESUMEN_URL = "/api/dashboard/presupuestos-resumen/"
EVOLUCION_MENSUAL_URL = "/api/dashboard/evolucion-mensual/"


class DashboardApiAuthTests(APITestCase):
    def test_evolucion_mensual_sin_autenticacion_devuelve_401(self):
        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_presupuestos_resumen_sin_autenticacion_devuelve_401(self):
        response = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 10, "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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


class DashboardPresupuestosResumenTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.client.force_authenticate(user=self.user)

        self.cat_alimentacion = Categoria.objects.create(
            usuario=self.user, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        self.cat_transporte = Categoria.objects.create(
            usuario=self.user, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )
        self.cat_entretenimiento = Categoria.objects.create(
            usuario=self.user, nombre="Entretenimiento", tipo=Categoria.Tipo.GASTO
        )

    def test_totales_y_porcentaje(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("100000.00"),
        )
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_transporte, mes=10, anio=2026,
            monto_limite=Decimal("50000.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("60000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_transporte, monto=Decimal("30000.00"),
            fecha="2026-10-10",
        )

        response = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["presupuesto_total"], "150000.00")
        self.assertEqual(response.data["gasto_real_presupuestado"], "90000.00")
        self.assertEqual(response.data["porcentaje_utilizado"], "60.00")

    def test_no_cuenta_gastos_de_categorias_sin_presupuesto(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("100000.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("50000.00"),
            fecha="2026-10-05",
        )
        # Entretenimiento no tiene presupuesto en el período: no debe sumar.
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_entretenimiento, monto=Decimal("20000.00"),
            fecha="2026-10-06",
        )

        response = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.data["gasto_real_presupuestado"], "50000.00")

    def test_separado_del_gasto_general_del_resumen(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("100000.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("50000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_entretenimiento, monto=Decimal("20000.00"),
            fecha="2026-10-06",
        )

        resumen = self.client.get(RESUMEN_URL, {"mes": 10, "anio": 2026})
        presupuestos_resumen = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(resumen.data["gastos"], "70000.00")
        self.assertEqual(presupuestos_resumen.data["gasto_real_presupuestado"], "50000.00")

    def test_sin_presupuestos_devuelve_ceros(self):
        response = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["presupuesto_total"], "0.00")
        self.assertEqual(response.data["gasto_real_presupuestado"], "0.00")
        self.assertEqual(response.data["porcentaje_utilizado"], "0.00")

    def test_parametros_invalidos_devuelve_400(self):
        response = self.client.get(PRESUPUESTOS_RESUMEN_URL, {"mes": 13, "anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardEvolucionMensualTests(APITestCase):
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

    def _mes(self, response, mes):
        return next(item for item in response.data["meses"] if item["mes"] == mes)

    def test_devuelve_doce_meses(self):
        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["meses"]), 12)
        self.assertEqual([m["mes"] for m in response.data["meses"]], list(range(1, 13)))

    # Agrupación correcta por mes. / Ingresos y gastos separados.
    def test_agrupacion_por_mes_ingresos_y_gastos_separados(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("150000.00"),
            fecha="2026-01-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("30000.00"),
            fecha="2026-01-10",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("160000.00"),
            fecha="2026-02-05",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        enero = self._mes(response, 1)
        febrero = self._mes(response, 2)
        self.assertEqual(enero["ingresos"], "150000.00")
        self.assertEqual(enero["gastos"], "30000.00")
        self.assertEqual(febrero["ingresos"], "160000.00")
        self.assertEqual(febrero["gastos"], "0.00")

    # Balance correcto.
    def test_balance_por_mes(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("150000.00"),
            fecha="2026-03-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("30000.00"),
            fecha="2026-03-10",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        marzo = self._mes(response, 3)
        self.assertEqual(marzo["balance"], "120000.00")

    # Meses sin movimientos.
    def test_meses_sin_movimientos_quedan_en_cero(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.00"),
            fecha="2026-06-05",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        for mes_data in response.data["meses"]:
            if mes_data["mes"] != 6:
                self.assertEqual(mes_data["ingresos"], "0.00")
                self.assertEqual(mes_data["gastos"], "0.00")
                self.assertEqual(mes_data["balance"], "0.00")

    def test_no_incluye_movimientos_de_otro_anio(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.00"),
            fecha="2025-06-05",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        junio = self._mes(response, 6)
        self.assertEqual(junio["ingresos"], "0.00")

    # Aislamiento entre usuarios.
    def test_no_incluye_movimientos_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=categoria_ajena, monto=Decimal("999999.00"),
            fecha="2026-04-05",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        abril = self._mes(response, 4)
        self.assertEqual(abril["ingresos"], "0.00")

    # Año inválido.
    def test_anio_faltante_devuelve_400(self):
        response = self.client.get(EVOLUCION_MENSUAL_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("anio", response.data)

    def test_anio_no_numerico_devuelve_400(self):
        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": "dosmilveintiseis"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anio_fuera_de_rango_devuelve_400(self):
        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 1800})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Precisión decimal.
    def test_precision_decimal(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.10"),
            fecha="2026-07-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("1000.20"),
            fecha="2026-07-06",
        )

        response = self.client.get(EVOLUCION_MENSUAL_URL, {"anio": 2026})

        julio = self._mes(response, 7)
        self.assertEqual(julio["ingresos"], "2000.30")
