from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categorias.models import Categoria

from ..models import Movimiento

LIST_URL = "/api/movimientos/"


def detail_url(pk):
    return f"/api/movimientos/{pk}/"


class MovimientoApiAuthTests(APITestCase):
    def test_listar_sin_autenticacion_devuelve_401(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_sin_autenticacion_devuelve_401(self):
        response = self.client.post(LIST_URL, {"monto": "100.00", "fecha": "2026-10-01"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MovimientoApiTests(APITestCase):
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
        self.cat_transporte = Categoria.objects.create(
            usuario=self.user, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )
        self.cat_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )

    # 1. Crear ingresos y gastos válidos.
    def test_crear_ingreso_valido(self):
        response = self.client.post(
            LIST_URL,
            {
                "categoria": self.cat_sueldo.id,
                "monto": "150000.00",
                "fecha": "2026-10-01",
                "descripcion": "Sueldo de octubre",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tipo"], "INGRESO")
        movimiento = Movimiento.objects.get()
        self.assertEqual(movimiento.usuario, self.user)

    def test_crear_gasto_valido(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_alimentacion.id, "monto": "5000.50", "fecha": "2026-10-02"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tipo"], "GASTO")

    def test_descripcion_es_opcional(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_sueldo.id, "monto": "100.00", "fecha": "2026-10-01"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_usuario_se_asigna_desde_request(self):
        response = self.client.post(
            LIST_URL,
            {
                "categoria": self.cat_sueldo.id,
                "monto": "100.00",
                "fecha": "2026-10-01",
                "usuario": self.otro_usuario.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movimiento.objects.get().usuario, self.user)

    # 2. Rechazar montos cero y negativos.
    def test_rechaza_monto_cero(self):
        response = self.client.post(
            LIST_URL, {"categoria": self.cat_sueldo.id, "monto": "0.00", "fecha": "2026-10-01"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monto", response.data)

    def test_rechaza_monto_negativo(self):
        response = self.client.post(
            LIST_URL, {"categoria": self.cat_sueldo.id, "monto": "-50.00", "fecha": "2026-10-01"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monto", response.data)

    # 3. Rechazar categorías de otro usuario.
    def test_rechaza_categoria_de_otro_usuario(self):
        response = self.client.post(
            LIST_URL,
            {"categoria": self.cat_ajena.id, "monto": "100.00", "fecha": "2026-10-01"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categoria", response.data)

    # 5. Editar movimientos.
    def test_editar_movimiento(self):
        movimiento = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("1000.00"),
            fecha="2026-10-01",
        )
        response = self.client.patch(detail_url(movimiento.id), {"monto": "2500.00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movimiento.refresh_from_db()
        self.assertEqual(movimiento.monto, Decimal("2500.00"))

    # 6. Eliminar movimientos.
    def test_eliminar_movimiento(self):
        movimiento = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("1000.00"),
            fecha="2026-10-01",
        )
        response = self.client.delete(detail_url(movimiento.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movimiento.objects.count(), 0)

    # 7. Impedir ver/editar/eliminar movimientos ajenos.
    def test_no_puede_ver_movimiento_ajeno(self):
        movimiento_ajeno = Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=self.cat_ajena, monto=Decimal("100.00"),
            fecha="2026-10-01",
        )
        response = self.client.get(detail_url(movimiento_ajeno.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_puede_editar_movimiento_ajeno(self):
        movimiento_ajeno = Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=self.cat_ajena, monto=Decimal("100.00"),
            fecha="2026-10-01",
        )
        response = self.client.patch(detail_url(movimiento_ajeno.id), {"monto": "1.00"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_puede_eliminar_movimiento_ajeno(self):
        movimiento_ajeno = Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=self.cat_ajena, monto=Decimal("100.00"),
            fecha="2026-10-01",
        )
        response = self.client.delete(detail_url(movimiento_ajeno.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Movimiento.objects.count(), 1)

    def test_listado_solo_incluye_movimientos_propios(self):
        Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("100.00"),
            fecha="2026-10-01",
        )
        Movimiento.objects.create(
            usuario=self.otro_usuario, categoria=self.cat_ajena, monto=Decimal("200.00"),
            fecha="2026-10-01",
        )
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class MovimientoFiltrosTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.client.force_authenticate(user=self.user)

        self.cat_sueldo = Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        self.cat_alimentacion = Categoria.objects.create(
            usuario=self.user, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )
        self.cat_transporte = Categoria.objects.create(
            usuario=self.user, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )

        self.mov_sueldo = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_sueldo, monto=Decimal("150000.00"),
            fecha="2026-10-01",
        )
        self.mov_alimentacion = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_alimentacion, monto=Decimal("5000.00"),
            fecha="2026-10-10",
        )
        self.mov_transporte = Movimiento.objects.create(
            usuario=self.user, categoria=self.cat_transporte, monto=Decimal("3000.00"),
            fecha="2026-10-20",
        )

    def _ids(self, response):
        return {item["id"] for item in response.data}

    # 8. Filtrar por fechas.
    def test_filtrar_por_fecha_desde(self):
        response = self.client.get(LIST_URL, {"fecha_desde": "2026-10-10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_alimentacion.id, self.mov_transporte.id})

    def test_filtrar_por_fecha_hasta(self):
        response = self.client.get(LIST_URL, {"fecha_hasta": "2026-10-10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_sueldo.id, self.mov_alimentacion.id})

    # 9. Filtrar por tipo.
    def test_filtrar_por_tipo_ingreso(self):
        response = self.client.get(LIST_URL, {"tipo": "INGRESO"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_sueldo.id})

    def test_filtrar_por_tipo_gasto(self):
        response = self.client.get(LIST_URL, {"tipo": "GASTO"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_alimentacion.id, self.mov_transporte.id})

    # 10. Filtrar por categoría.
    def test_filtrar_por_categoria(self):
        response = self.client.get(LIST_URL, {"categoria": self.cat_transporte.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_transporte.id})

    # 11. Combinar filtros.
    def test_combinar_filtros_tipo_y_fecha(self):
        response = self.client.get(
            LIST_URL, {"tipo": "GASTO", "fecha_desde": "2026-10-15"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._ids(response), {self.mov_transporte.id})

    def test_orden_por_fecha_mas_reciente_primero(self):
        response = self.client.get(LIST_URL)
        fechas = [item["fecha"] for item in response.data]
        self.assertEqual(fechas, sorted(fechas, reverse=True))

    # 12. Validar fechas inválidas y rangos inconsistentes.
    def test_fecha_desde_invalida_devuelve_400(self):
        response = self.client.get(LIST_URL, {"fecha_desde": "no-es-una-fecha"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fecha_desde", response.data)

    def test_fecha_hasta_invalida_devuelve_400(self):
        response = self.client.get(LIST_URL, {"fecha_hasta": "2026-99-99"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fecha_hasta", response.data)

    def test_rango_de_fechas_inconsistente_devuelve_400(self):
        response = self.client.get(
            LIST_URL, {"fecha_desde": "2026-10-20", "fecha_hasta": "2026-10-01"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fecha_desde", response.data)

    def test_tipo_invalido_devuelve_400(self):
        response = self.client.get(LIST_URL, {"tipo": "AHORRO"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tipo", response.data)

    def test_categoria_no_numerica_devuelve_400(self):
        response = self.client.get(LIST_URL, {"categoria": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categoria", response.data)
