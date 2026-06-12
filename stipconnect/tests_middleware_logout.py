"""Tests for Cloudflare Access Middleware auto-creating Profile + Logout View."""
import os
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware

from stipconnect.middleware import CloudflareAccessMiddleware
from profiles.models import Profile

User = get_user_model()

class MiddlewareProfileAutoCreateTestCase(TestCase):
    """Middleware must auto-create Profile when creating a new User."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CloudflareAccessMiddleware(lambda req: "ok")

    def _add_session(self, request):
        """Add session support to the request so login() works."""
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        return request

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.settings')
    def test_new_user_gets_profile_created(self, mock_settings, mock_login):
        """Fresh CF Access login -> User + Profile both created."""
        mock_settings.DEBUG = True
        request = self.factory.get('/')
        request.META['HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL'] = 'newuser@sdw.de'
        request.user = MagicMock()
        request.user.is_authenticated = False
        request = self._add_session(request)

        response = self.middleware(request)
        self.assertEqual(response, "ok")

        # Verify user exists
        user = User.objects.get(username='newuser@sdw.de')
        self.assertEqual(user.email, 'newuser@sdw.de')

        # Verify profile was auto-created by middleware
        self.assertTrue(Profile.objects.filter(user=user).exists())
        profile = user.profile
        self.assertFalse(profile.consent_given)
        self.assertFalse(profile.pending)
        mock_login.assert_called_once()

    @patch('stipconnect.middleware.login')
    @patch('stipconnect.middleware.settings')
    def test_existing_user_profile_not_duplicated(self, mock_settings, mock_login):
        """Returning user -> Profile NOT duplicated, login still called."""
        mock_settings.DEBUG = True
        user = User.objects.create_user(username='existing@sdw.de', email='existing@sdw.de')
        Profile.objects.get_or_create(user=user)

        request = self.factory.get('/')
        request.META['HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL'] = 'existing@sdw.de'
        request.user = MagicMock()
        request.user.is_authenticated = False
        request = self._add_session(request)

        response = self.middleware(request)
        self.assertEqual(response, "ok")

        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        mock_login.assert_called_once()


class LogoutViewTestCase(TestCase):
    """Tests for the custom LogoutView."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='logouttest@sdw.de', email='logouttest@sdw.de')
        Profile.objects.get_or_create(user=self.user)

    def test_logout_get_redirects_home(self):
        """GET /accounts/logout/ clears session and redirects to Cloudflare logout."""
        self.client.force_login(self.user)
        self.assertIn('_auth_user_id', self.client.session)

        resp = self.client.get('/accounts/logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'https://sdw-connect.kochlab.net/cdn-cgi/access/logout')
        # Session cleared
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_post_redirects_home(self):
        """POST /accounts/logout/ returns 405 (only GET supported)."""
        self.client.force_login(self.user)
        resp = self.client.post('/accounts/logout/')
        self.assertEqual(resp.status_code, 405)

    def test_logout_when_not_logged_in(self):
        """Logout without active session still redirects to CF logout."""
        resp = self.client.get('/accounts/logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'https://sdw-connect.kochlab.net/cdn-cgi/access/logout')
