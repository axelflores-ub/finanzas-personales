import inspect
import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from config.settings import _env_bool
import config.settings as settings_module


class SettingsSeguraPorDefectoTests(SimpleTestCase):
    """DEBUG debe arrancar en False si falta DJANGO_DEBUG en el entorno.

    No se puede simplemente releer `settings.DEBUG` acá, porque Django ya
    cargó el módulo de settings una vez al arrancar el proceso de test (con
    `backend/.env`, que sí define DJANGO_DEBUG=True a propósito para
    desarrollo). Lo que sí se puede probar sin recargar Django es la función
    que calcula ese valor (`_env_bool`) con la variable ausente, que es
    exactamente lo que hace la línea `DEBUG = _env_bool("DJANGO_DEBUG",
    "False")` en settings.py.
    """

    def test_env_bool_devuelve_false_si_la_variable_no_existe(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_env_bool("DJANGO_DEBUG_VARIABLE_INEXISTENTE", "False"))

    def test_env_bool_respeta_el_valor_explicito_de_la_variable(self):
        with mock.patch.dict(os.environ, {"DJANGO_DEBUG_VARIABLE_INEXISTENTE": "True"}):
            self.assertTrue(_env_bool("DJANGO_DEBUG_VARIABLE_INEXISTENTE", "False"))

    def test_debug_usa_false_como_default_en_el_codigo_fuente(self):
        """Guarda de regresión: si alguien vuelve a poner "True" como default
        de DJANGO_DEBUG en settings.py, este test debe fallar.
        """
        fuente = inspect.getsource(settings_module)
        self.assertIn('_env_bool("DJANGO_DEBUG", "False")', fuente)


class HealthCheckTests(APITestCase):
    def test_health_check_es_publico_y_responde_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["database"], "ok")


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.username = "usuario_test"
        self.password = "clave-de-prueba-123"
        self.user = get_user_model().objects.create_user(
            username=self.username, password=self.password
        )

    def test_endpoint_protegido_sin_token_devuelve_401(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtener_token_con_credenciales_validas(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtener_token_con_credenciales_invalidas_devuelve_401(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": self.username, "password": "incorrecta"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoint_protegido_con_token_valido_devuelve_usuario(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": self.username, "password": self.password},
        )
        access_token = token_response.data["access"]

        response = self.client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.username)

    def test_refrescar_token(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": self.username, "password": self.password},
        )
        refresh_token = token_response.data["refresh"]

        response = self.client.post(
            "/api/auth/token/refresh/", {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
