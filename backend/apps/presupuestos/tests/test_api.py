from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento

from ..models import Presupuesto

LIST_URL = "/api/presupuestos/"


def detail_url(pk):
    return f"/api/presupuestos/{pk}/"


class PresupuestoApiAuthTests(APITestCase):
    def test_listar_sin_autenticacion_devuelve_401(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_sin_autenticacion_devuelve_401(self):
        response = self.client.post(LIST_URL, {"mes": 10, "anio": 2026, "monto_limite": "1.00"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PresupuestoApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.otro_usuario = get_user_model().objects.create_user(username="beto", password="x")
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

    # 1. CRUD completo.
    def test_crear_presupuesto_valido(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_alimentacion.id, "mes": 10, "anio": 2026, "monto_limite": "150000.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Presupuesto.objects.get().usuario, self.user)

    def test_usuario_se_asigna_desde_request(self):
        response = self.client.post(
            LIST_URL,
            {
                "categoria": self.cat_alimentacion.id,
                "mes": 10,
                "anio": 2026,
                "monto_limite": "1000.00",
                "usuario": self.otro_usuario.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Presupuesto.objects.get().usuario, self.user)

    def test_listar_presupuestos(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_editar_presupuesto(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.patch(detail_url(presupuesto.id), {"monto_limite": "2000.00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        presupuesto.refresh_from_db()
        self.assertEqual(presupuesto.monto_limite, Decimal("2000.00"))

    def test_patch_con_limite_invalido_rechazado_y_no_altera_el_dato(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.patch(detail_url(presupuesto.id), {"monto_limite": "0.00"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monto_limite", response.data)
        presupuesto.refresh_from_db()
        self.assertEqual(presupuesto.monto_limite, Decimal("1000.00"))

    def test_patch_con_limite_negativo_rechazado_y_no_altera_el_dato(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.patch(detail_url(presupuesto.id), {"monto_limite": "-250.00"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monto_limite", response.data)
        presupuesto.refresh_from_db()
        self.assertEqual(presupuesto.monto_limite, Decimal("1000.00"))

    def test_patch_con_categoria_de_ingreso_rechazado_y_no_altera_el_dato(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.patch(detail_url(presupuesto.id), {"categoria": self.cat_sueldo.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categoria", response.data)
        presupuesto.refresh_from_db()
        self.assertEqual(presupuesto.categoria_id, self.cat_alimentacion.id)

    def test_eliminar_presupuesto(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.delete(detail_url(presupuesto.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Presupuesto.objects.count(), 0)

    # 2. Categoría de ingreso rechazada.
    def test_rechaza_categoria_de_ingreso(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_sueldo.id, "mes": 10, "anio": 2026, "monto_limite": "1000.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categoria", response.data)

    # 3. Categoría de otro usuario rechazada.
    def test_rechaza_categoria_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        response = self.client.post(
            LIST_URL,
            {"categoria": categoria_ajena.id, "mes": 10, "anio": 2026, "monto_limite": "1000.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categoria", response.data)

    # 4. Presupuesto duplicado rechazado.
    def test_rechaza_presupuesto_duplicado(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_alimentacion.id, "mes": 10, "anio": 2026, "monto_limite": "500.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 5. Límite cero o negativo rechazado.
    def test_rechaza_limite_cero(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_alimentacion.id, "mes": 10, "anio": 2026, "monto_limite": "0.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rechaza_limite_negativo(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_alimentacion.id, "mes": 10, "anio": 2026, "monto_limite": "-100.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 7. Aislamiento entre usuarios.
    def test_no_puede_ver_presupuesto_ajeno(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        presupuesto_ajeno = Presupuesto.objects.create(
            usuario=self.otro_usuario, categoria=categoria_ajena, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        response = self.client.get(detail_url(presupuesto_ajeno.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_puede_editar_ni_eliminar_presupuesto_ajeno(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        presupuesto_ajeno = Presupuesto.objects.create(
            usuario=self.otro_usuario, categoria=categoria_ajena, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        self.assertEqual(
            self.client.patch(detail_url(presupuesto_ajeno.id), {"monto_limite": "1.00"}).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.delete(detail_url(presupuesto_ajeno.id)).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(Presupuesto.objects.count(), 1)

    def test_listado_solo_incluye_presupuestos_propios(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        Presupuesto.objects.create(
            usuario=self.otro_usuario, categoria=categoria_ajena, mes=10, anio=2026,
            monto_limite=Decimal("2000.00"),
        )
        response = self.client.get(LIST_URL)
        self.assertEqual(len(response.data), 1)

    # 8. Cálculo correcto del gasto real. / 9. Porcentaje de utilización.
    def test_gasto_real_y_porcentaje(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("150000.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("60000.00"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("30000.00"),
            fecha="2026-10-15",
        )

        response = self.client.get(detail_url(presupuesto.id))

        self.assertEqual(response.data["gasto_real"], "90000.00")
        self.assertEqual(response.data["porcentaje_utilizado"], "60.00")
        self.assertEqual(response.data["restante"], "60000.00")

    # 10. Presupuesto superado.
    def test_presupuesto_superado(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("10000.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("15000.00"),
            fecha="2026-10-05",
        )

        response = self.client.get(detail_url(presupuesto.id))

        self.assertEqual(response.data["gasto_real"], "15000.00")
        self.assertEqual(response.data["porcentaje_utilizado"], "150.00")
        self.assertEqual(response.data["restante"], "-5000.00")

    # 11. Presupuesto sin movimientos.
    def test_presupuesto_sin_movimientos(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("10000.00"),
        )

        response = self.client.get(detail_url(presupuesto.id))

        self.assertEqual(response.data["gasto_real"], "0.00")
        self.assertEqual(response.data["porcentaje_utilizado"], "0.00")
        self.assertEqual(response.data["restante"], "10000.00")

    # 12. Actualización del gasto al crear, editar y eliminar movimientos.
    def test_gasto_real_se_actualiza_con_movimientos(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("10000.00"),
        )

        self.assertEqual(self.client.get(detail_url(presupuesto.id)).data["gasto_real"], "0.00")

        movimiento = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("4000.00"),
            fecha="2026-10-05",
        )
        self.assertEqual(self.client.get(detail_url(presupuesto.id)).data["gasto_real"], "4000.00")

        movimiento.monto = Decimal("7000.00")
        movimiento.save()
        self.assertEqual(self.client.get(detail_url(presupuesto.id)).data["gasto_real"], "7000.00")

        movimiento.delete()
        self.assertEqual(self.client.get(detail_url(presupuesto.id)).data["gasto_real"], "0.00")

    # 13. Filtros por mes y año.
    def test_filtra_por_mes_y_anio(self):
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("1000.00"),
        )
        Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_transporte, mes=11, anio=2026,
            monto_limite=Decimal("2000.00"),
        )

        response = self.client.get(LIST_URL, {"mes": 10, "anio": 2026})

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["categoria_nombre"], "Alimentación")

    # 14. Precisión decimal.
    def test_precision_decimal(self):
        presupuesto = Presupuesto.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, mes=10, anio=2026,
            monto_limite=Decimal("300.00"),
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("100.10"),
            fecha="2026-10-05",
        )
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("100.20"),
            fecha="2026-10-06",
        )

        response = self.client.get(detail_url(presupuesto.id))

        self.assertEqual(response.data["gasto_real"], "200.30")
        self.assertEqual(response.data["restante"], "99.70")
