from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


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
