"""Unit tests for CloudflareAccessMiddleware in isolation."""
import os
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory

from stipconnect.middleware import CloudflareAccessMiddleware


class CloudflareAccessMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CloudflareAccessMiddleware(lambda req: "ok")

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.User.objects.get_or_create')
    @patch('stipconnect.middleware.settings')
    def test_debug_fallback_dev_auth_email(
        self, mock_settings, mock_get_or_create, mock_login
    ):
        """DEBUG + kein Header -> DEV_AUTH_EMAIL wird benutzt."""
        mock_settings.DEBUG = True
        with patch.dict(os.environ, {"DEV_AUTH_EMAIL": "dev@test.com"}, clear=True):
            request = self.factory.get('/')
            request.user = MagicMock()
            request.user.is_authenticated = False
            mock_user = MagicMock()
            mock_get_or_create.return_value = (mock_user, True)

            response = self.middleware(request)

            self.assertEqual(response, "ok")
            mock_get_or_create.assert_called_once_with(
                username="dev@test.com",
                defaults={
                    'email': "dev@test.com",
                    'first_name': '',
                    'last_name': '',
                },
            )
            mock_login.assert_called_once_with(
                request, mock_user, backend='django.contrib.auth.backends.ModelBackend'
            )

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.User.objects.get_or_create')
    @patch('stipconnect.middleware.settings')
    def test_debug_header_priority(
        self, mock_settings, mock_get_or_create, mock_login
    ):
        """DEBUG + Header vorhanden -> Header gewinnt, DEV_AUTH_EMAIL ignoriert."""
        mock_settings.DEBUG = True
        with patch.dict(os.environ, {"DEV_AUTH_EMAIL": "env@test.com"}):
            request = self.factory.get('/')
            request.META['HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL'] = "head@test.com"
            request.user = MagicMock()
            request.user.is_authenticated = False
            mock_user = MagicMock()
            mock_get_or_create.return_value = (mock_user, False)

            self.middleware(request)

            mock_get_or_create.assert_called_once_with(
                username="head@test.com",
                defaults={
                    'email': "head@test.com",
                    'first_name': '',
                    'last_name': '',
                },
            )
            mock_login.assert_called_once()

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.settings')
    def test_production_missing_header(self, mock_settings, mock_login):
        """DEBUG=False + kein Header -> App bleibt offen (Cloudflare Access blockiert extern)."""
        mock_settings.DEBUG = False
        request = self.factory.get('/')
        request.user = MagicMock()
        request.user.is_authenticated = False

        response = self.middleware(request)

        self.assertEqual(response, "ok")
        mock_login.assert_not_called()

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.User.objects.get_or_create')
    @patch('stipconnect.middleware.settings')
    def test_production_valid_header(
        self, mock_settings, mock_get_or_create, mock_login
    ):
        """DEBUG=False + Header -> Benutzer wird erstellt/eingeloggt."""
        mock_settings.DEBUG = False
        request = self.factory.get('/')
        request.META['HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL'] = "cf@test.com"
        request.user = MagicMock()
        request.user.is_authenticated = False
        mock_user = MagicMock()
        mock_get_or_create.return_value = (mock_user, False)

        response = self.middleware(request)

        self.assertEqual(response, "ok")
        mock_get_or_create.assert_called_once_with(
            username="cf@test.com",
            defaults={
                'email': "cf@test.com",
                'first_name': '',
                'last_name': '',
            },
        )
        mock_login.assert_called_once()

    def test_already_authenticated(self):
        """Bereits authentifiziert -> Middleware tut nichts."""
        request = self.factory.get('/')
        request.user = MagicMock()
        request.user.is_authenticated = True

        response = self.middleware(request)
        self.assertEqual(response, "ok")
