from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Categoria


class CategoriaModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")

    def test_categoria_unica_por_usuario_nombre_tipo(self):
        Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Categoria.objects.create(
                    usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
                )

    def test_mismo_nombre_distinto_tipo_permitido(self):
        Categoria.objects.create(
            usuario=self.user, nombre="Otros", tipo=Categoria.Tipo.INGRESO
        )
        Categoria.objects.create(
            usuario=self.user, nombre="Otros", tipo=Categoria.Tipo.GASTO
        )
        self.assertEqual(Categoria.objects.filter(nombre="Otros").count(), 2)

    def test_mismo_nombre_y_tipo_en_otro_usuario_permitido(self):
        otro_usuario = get_user_model().objects.create_user(username="beto", password="x")
        Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        Categoria.objects.create(
            usuario=otro_usuario, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )
        self.assertEqual(Categoria.objects.filter(nombre="Sueldo").count(), 2)
