from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from apps.categorias.models import Categoria

from .models import Presupuesto


class PresupuestoModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.categoria_gasto = Categoria.objects.create(
            usuario=self.user, nombre="Vivienda", tipo=Categoria.Tipo.GASTO
        )
        self.categoria_ingreso = Categoria.objects.create(
            usuario=self.user, nombre="Sueldo", tipo=Categoria.Tipo.INGRESO
        )

    def test_presupuesto_valido(self):
        presupuesto = Presupuesto(
            usuario=self.user,
            categoria=self.categoria_gasto,
            mes=10,
            anio=2026,
            monto_limite=Decimal("50000.00"),
        )
        presupuesto.full_clean()
        presupuesto.save()
        self.assertEqual(Presupuesto.objects.count(), 1)

    def test_categoria_de_tipo_ingreso_rechazada(self):
        presupuesto = Presupuesto(
            usuario=self.user,
            categoria=self.categoria_ingreso,
            mes=10,
            anio=2026,
            monto_limite=Decimal("50000.00"),
        )
        with self.assertRaises(ValidationError):
            presupuesto.full_clean()

    def test_monto_limite_debe_ser_positivo(self):
        presupuesto = Presupuesto(
            usuario=self.user,
            categoria=self.categoria_gasto,
            mes=10,
            anio=2026,
            monto_limite=Decimal("0.00"),
        )
        with self.assertRaises(ValidationError):
            presupuesto.full_clean()

    def test_unico_por_usuario_categoria_mes_anio(self):
        Presupuesto.objects.create(
            usuario=self.user,
            categoria=self.categoria_gasto,
            mes=10,
            anio=2026,
            monto_limite=Decimal("50000.00"),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Presupuesto.objects.create(
                    usuario=self.user,
                    categoria=self.categoria_gasto,
                    mes=10,
                    anio=2026,
                    monto_limite=Decimal("20000.00"),
                )

    def test_no_se_puede_borrar_categoria_con_presupuesto(self):
        Presupuesto.objects.create(
            usuario=self.user,
            categoria=self.categoria_gasto,
            mes=10,
            anio=2026,
            monto_limite=Decimal("50000.00"),
        )
        with self.assertRaises(ProtectedError):
            self.categoria_gasto.delete()
