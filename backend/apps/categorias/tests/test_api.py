from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categorias.models import Categoria
from apps.movimientos.models import Movimiento

LIST_URL = "/api/categorias/"


def detail_url(pk):
    return f"/api/categorias/{pk}/"


class CategoriaApiAuthTests(APITestCase):
    def test_listar_sin_autenticacion_devuelve_401(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_sin_autenticacion_devuelve_401(self):
        response = self.client.post(LIST_URL, {"nombre": "Sueldo", "tipo": "INGRESO"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoriaApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.otro_usuario = get_user_model().objects.create_user(username="beto", password="x")
        self.client.force_authenticate(user=self.user)

    def test_crear_categoria_valida(self):
        response = self.client.post(LIST_URL, {"nombre": "Sueldo", "tipo": "INGRESO"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 1)
        categoria = Categoria.objects.get()
        self.assertEqual(categoria.usuario, self.user)
        self.assertEqual(categoria.nombre, "Sueldo")

    def test_usuario_se_asigna_desde_request_no_desde_el_body(self):
        response = self.client.post(
            LIST_URL,
            {"nombre": "Sueldo", "tipo": "INGRESO", "usuario": self.otro_usuario.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        categoria = Categoria.objects.get()
        self.assertEqual(categoria.usuario, self.user)

    def test_rechaza_categoria_duplicada(self):
        Categoria.objects.create(usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO)
        response = self.client.post(LIST_URL, {"nombre": "Sueldo", "tipo": "INGRESO"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nombre", response.data)

    def test_rechaza_nombre_vacio(self):
        response = self.client.post(LIST_URL, {"nombre": "", "tipo": "INGRESO"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nombre", response.data)

    def test_rechaza_tipo_invalido(self):
        response = self.client.post(LIST_URL, {"nombre": "Varios", "tipo": "AHORRO"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tipo", response.data)

    def test_editar_categoria(self):
        categoria = Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        response = self.client.patch(detail_url(categoria.id), {"nombre": "Sueldo mensual"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, "Sueldo mensual")

    def test_eliminar_categoria_sin_relaciones(self):
        categoria = Categoria.objects.create(
            usuario=self.user, nombre="Entretenimiento", tipo=Categoria.Tipo.GASTO
        )
        response = self.client.delete(detail_url(categoria.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Categoria.objects.count(), 0)

    def test_rechaza_eliminar_categoria_con_movimientos(self):
        categoria = Categoria.objects.create(
            usuario=self.user, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )
        Movimiento.objects.create(
            usuario=self.user,
            categoria=categoria,
            monto=Decimal("1000.00"),
            fecha="2026-10-01",
        )
        response = self.client.delete(detail_url(categoria.id))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Categoria.objects.count(), 1)

    def test_no_puede_ver_categoria_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        response = self.client.get(detail_url(categoria_ajena.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_puede_editar_categoria_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        response = self.client.patch(detail_url(categoria_ajena.id), {"nombre": "Hackeado"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_puede_eliminar_categoria_de_otro_usuario(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        response = self.client.delete(detail_url(categoria_ajena.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Categoria.objects.count(), 1)

    def test_listado_solo_incluye_categorias_propias(self):
        Categoria.objects.create(usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO)
        Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Alquiler", tipo=Categoria.Tipo.GASTO
        )
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [c["nombre"] for c in response.data]
        self.assertEqual(nombres, ["Sueldo"])
