from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from apps.categorias.models import Categoria

from ..models import Movimiento


class MovimientoModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ana", password="x")
        self.otro_usuario = get_user_model().objects.create_user(username="beto", password="x")
        self.categoria_gasto = Categoria.objects.create(
            usuario=self.user, nombre="Alimentación", tipo=Categoria.Tipo.GASTO
        )

    def test_movimiento_valido(self):
        movimiento = Movimiento(
            usuario=self.user,
            categoria=self.categoria_gasto,
            monto=Decimal("1500.50"),
            fecha="2026-10-01",
        )
        movimiento.full_clean()
        movimiento.save()
        self.assertEqual(Movimiento.objects.count(), 1)

    def test_monto_negativo_rechazado_por_validacion(self):
        movimiento = Movimiento(
            usuario=self.user,
            categoria=self.categoria_gasto,
            monto=Decimal("-10.00"),
            fecha="2026-10-01",
        )
        with self.assertRaises(ValidationError):
            movimiento.full_clean()

    def test_monto_cero_rechazado_por_constraint_de_bd(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Movimiento.objects.create(
                    usuario=self.user,
                    categoria=self.categoria_gasto,
                    monto=Decimal("0.00"),
                    fecha="2026-10-01",
                )

    def test_categoria_de_otro_usuario_rechazada(self):
        categoria_ajena = Categoria.objects.create(
            usuario=self.otro_usuario, nombre="Transporte", tipo=Categoria.Tipo.GASTO
        )
        movimiento = Movimiento(
            usuario=self.user,
            categoria=categoria_ajena,
            monto=Decimal("100.00"),
            fecha="2026-10-01",
        )
        with self.assertRaises(ValidationError):
            movimiento.full_clean()

    def test_no_se_puede_borrar_categoria_con_movimientos(self):
        Movimiento.objects.create(
            usuario=self.user,
            categoria=self.categoria_gasto,
            monto=Decimal("50.00"),
            fecha="2026-10-01",
        )
        with self.assertRaises(ProtectedError):
            self.categoria_gasto.delete()
