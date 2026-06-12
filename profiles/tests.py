"""Tests für die Swipe-API Endpoints."""
import json

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from profiles.swipe_views import ProfileBatchView, SwipeFeedView, SwipeActionView, MatchListView
from profiles.models import Profile, Swipe


class ProfileBatchViewTestCase(TestCase):
    """GET /api/profiles/ — 10 ungesehene Profile."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = ProfileBatchView.as_view()

        # Haupt-User (swiped)
        self.user = User.objects.create_user(
            username='swiper@test.com',
            email='swiper@test.com',
            first_name='Swiper',
            last_name='Fox',
        )
        self.profile = self.user.profile
        self.profile.consent_given = True
        self.profile.visible = True
        self.profile.pending = False
        self.profile.is_beta_tester = True
        self.profile.gender = 'M'
        self.profile.seeking = 'F'
        self.profile.studienfach = 'Wirtschaftsing.'
        self.profile.hochschule = 'FH Erfurt'
        self.profile.save()

        # Ziel-Profile (weiblich, suchen Männer, sichtbar)
        self.target_users = []
        for i in range(12):
            u = User.objects.create_user(
                username=f'target{i}@test.com',
                email=f'target{i}@test.com',
                first_name='Target',
                last_name=f'{i}',
            )
            p = u.profile
            p.consent_given = True
            p.visible = True
            p.pending = False
            p.is_beta_tester = True
            p.gender = 'F'
            p.seeking = 'M'
            p.studienfach = f'Fach {i}'
            p.hochschule = f'Uni {i}'
            p.quote = f'Spruch {i}'
            p.photos = [f'https://example.com/photo{i}.jpg']
            p.save()
            self.target_users.append((u, p))

        # Ein Profil bereits geswiped (like)
        self.swiped_user, self.swiped_profile = self.target_users[0]
        Swipe.objects.create(from_user=self.user, to_user=self.swiped_user, decision='like')

        # Ein Profil unsichtbar
        self.hidden_user, self.hidden_profile = self.target_users[1]
        self.hidden_profile.visible = False
        self.hidden_profile.save()

        # Ein Profil pending
        self.pending_user, self.pending_profile = self.target_users[2]
        self.pending_profile.pending = True
        self.pending_profile.save()

        # Ein Profil ohne Consent
        self.no_consent_user, self.no_consent_profile = self.target_users[3]
        self.no_consent_profile.consent_given = False
        self.no_consent_profile.save()

    def _auth_request(self, method='get', url='/api/profiles/', data=None, **kwargs):
        if method == 'get':
            request = self.factory.get(url, data=data or {})
        else:
            request = self.factory.post(url, data=json.dumps(data or {}), content_type='application/json')
        request.user = self.user
        return self.view(request, **kwargs)

    def test_returns_10_profiles_default(self):
        """Standardmäßig bis zu 10 Profile zurückgeben."""
        response = self._auth_request()
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('profiles', payload)
        # 12 targets - 4 excluded = 8 available (geswiped, hidden, pending, no-consent)
        self.assertEqual(payload['count'], 8)
        self.assertEqual(len(payload['profiles']), 8)

    def test_excludes_own_profile(self):
        """Eigenes Profil darf nicht im Feed sein."""
        response = self._auth_request()
        payload = json.loads(response.content)
        ids = [p['id'] for p in payload['profiles']]
        self.assertNotIn(self.user.id, ids)

    def test_excludes_already_swiped(self):
        """Bereits geswipete Profile dürfen nicht im Feed sein."""
        response = self._auth_request()
        payload = json.loads(response.content)
        ids = [p['id'] for p in payload['profiles']]
        self.assertNotIn(self.swiped_user.id, ids)

    def test_excludes_hidden_pending_no_consent(self):
        """Unsichtbare, pending und no-consent Profile ausschließen."""
        response = self._auth_request()
        payload = json.loads(response.content)
        ids = [p['id'] for p in payload['profiles']]
        self.assertNotIn(self.hidden_user.id, ids)
        self.assertNotIn(self.pending_user.id, ids)
        self.assertNotIn(self.no_consent_user.id, ids)

    def test_limit_param_respected(self):
        """Limit-Parameter wird beachtet (z.B. limit=5)."""
        response = self._auth_request(data={'limit': '5'})
        payload = json.loads(response.content)
        self.assertEqual(payload['count'], 5)
        self.assertEqual(len(payload['profiles']), 5)

    def test_limit_max_50(self):
        """Limit über 50 wird auf 10 zurückgesetzt."""
        response = self._auth_request(data={'limit': '100'})
        payload = json.loads(response.content)
        # 8 verfügbare Profile (12 - 4 excluded)
        self.assertEqual(payload['count'], 8)

    def test_limit_invalid_defaults_to_10(self):
        """Ungültiger Limit-Wert -> default 10."""
        response = self._auth_request(data={'limit': 'abc'})
        payload = json.loads(response.content)
        # 8 verfügbare Profile (12 - 4 excluded)
        self.assertEqual(payload['count'], 8)

    def test_returns_empty_array_when_none_left(self):
        """Wenn keine Profile übrig: leeres Array, count 0."""
        visible_targets = [
            (u, p) for u, p in self.target_users
            if p.visible and not p.pending and p.consent_given and u != self.user and u != self.swiped_user
        ]
        for u, _ in visible_targets:
            Swipe.objects.create(from_user=self.user, to_user=u, decision='pass')
        response = self._auth_request()
        payload = json.loads(response.content)
        self.assertEqual(payload['count'], 0)
        self.assertEqual(payload['profiles'], [])

    def test_profile_fields_present(self):
        """Jedes Profil hat die erwarteten Felder."""
        response = self._auth_request(data={'limit': '1'})
        payload = json.loads(response.content)
        p = payload['profiles'][0]
        expected = {'id', 'profile_id', 'name', 'age', 'quote', 'about', 'photo',
                    'photos', 'studienfach', 'hochschule', 'interests', 'gender'}
        self.assertTrue(expected.issubset(set(p.keys())))

    def test_403_if_no_consent(self):
        """User ohne Consent -> 403."""
        self.profile.consent_given = False
        self.profile.save()
        response = self._auth_request()
        self.assertEqual(response.status_code, 403)

    def test_403_if_not_visible(self):
        """User nicht visible -> 403."""
        self.profile.visible = False
        self.profile.save()
        response = self._auth_request()
        self.assertEqual(response.status_code, 403)

    def test_302_if_pending(self):
        """User pending -> Redirect zur Warteschlange (302)."""
        self.profile.pending = True
        self.profile.save()
        response = self._auth_request()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/warteschlange/')

    def test_gender_filter_applied(self):
        """Nur Profile passenden Geschlechts werden zurückgegeben."""
        response = self._auth_request()
        payload = json.loads(response.content)
        for p in payload['profiles']:
            self.assertEqual(p['gender'], 'Frau')

    def test_only_visible_interests_included(self):
        """Interessen-Feld ist immer als Array vorhanden."""
        response = self._auth_request(data={'limit': '1'})
        payload = json.loads(response.content)
        p = payload['profiles'][0]
        self.assertIsInstance(p['interests'], list)


class SwipeFeedViewTestCase(TestCase):
    """GET /api/swipe/next/ — einzelnes Profil."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = SwipeFeedView.as_view()

        self.user = User.objects.create_user(
            username='u1@test.com', email='u1@test.com', first_name='A', last_name='B'
        )
        self.profile = self.user.profile
        self.profile.consent_given = True
        self.profile.visible = True
        self.profile.pending = False
        self.profile.is_beta_tester = True
        self.profile.gender = 'M'
        self.profile.seeking = 'F'
        self.profile.save()

        self.target = User.objects.create_user(
            username='t1@test.com', email='t1@test.com', first_name='T', last_name='1'
        )
        self.target_profile = self.target.profile
        self.target_profile.consent_given = True
        self.target_profile.visible = True
        self.target_profile.pending = False
        self.target_profile.is_beta_tester = True
        self.target_profile.gender = 'F'
        self.target_profile.seeking = 'M'
        self.target_profile.quote = 'Hallo'
        self.target_profile.photos = ['url.jpg']
        self.target_profile.save()

    def _auth_request(self):
        request = self.factory.get('/api/swipe/next/')
        request.user = self.user
        return self.view(request)

    def test_returns_single_profile(self):
        response = self._auth_request()
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn('id', payload)
        self.assertEqual(payload['name'], 'T 1')

    def test_empty_when_none_left(self):
        Swipe.objects.create(from_user=self.user, to_user=self.target, decision='pass')
        response = self._auth_request()
        payload = json.loads(response.content)
        self.assertTrue(payload.get('empty'))


class SwipeActionViewTestCase(TestCase):
    """POST /api/swipe/action/ — Like/Pass."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = SwipeActionView.as_view()

        self.user = User.objects.create_user(
            username='u1@test.com', email='u1@test.com', first_name='A', last_name='B'
        )
        self.user_profile = self.user.profile
        self.user_profile.consent_given = True
        self.user_profile.visible = True
        self.user_profile.pending = False
        self.user_profile.is_beta_tester = True
        self.user_profile.save()

        self.target = User.objects.create_user(
            username='t1@test.com', email='t1@test.com', first_name='T', last_name='1'
        )
        self.target_profile = self.target.profile
        self.target_profile.consent_given = True
        self.target_profile.visible = True
        self.target_profile.pending = False
        self.target_profile.is_beta_tester = True
        self.target_profile.save()

    def _auth_post(self, data):
        request = self.factory.post(
            '/api/swipe/action/',
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        return self.view(request)

    def test_like_creates_swipe(self):
        response = self._auth_post({'to_user_id': self.target.id, 'decision': 'like'})
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['success'])
        self.assertFalse(payload['match'])

    def test_pass_creates_swipe(self):
        response = self._auth_post({'to_user_id': self.target.id, 'decision': 'pass'})
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['success'])

    def test_match_detected(self):
        Swipe.objects.create(from_user=self.target, to_user=self.user, decision='like')
        response = self._auth_post({'to_user_id': self.target.id, 'decision': 'like'})
        payload = json.loads(response.content)
        self.assertTrue(payload['match'])
        self.assertIn('match_data', payload)

    def test_invalid_decision_400(self):
        response = self._auth_post({'to_user_id': self.target.id, 'decision': 'maybe'})
        self.assertEqual(response.status_code, 400)

    def test_missing_user_400(self):
        response = self._auth_post({'decision': 'like'})
        self.assertEqual(response.status_code, 400)


class MatchListViewTestCase(TestCase):
    """GET /api/matches/ — gegenseitige Likes."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = MatchListView.as_view()

        self.user = User.objects.create_user(
            username='u1@test.com', email='u1@test.com', first_name='A', last_name='B'
        )
        self.user_profile = self.user.profile
        self.user_profile.consent_given = True
        self.user_profile.visible = True
        self.user_profile.pending = False
        self.user_profile.is_beta_tester = True
        self.user_profile.save()

        self.match = User.objects.create_user(
            username='match@test.com', email='match@test.com', first_name='M', last_name='X'
        )
        self.match_profile = self.match.profile
        self.match_profile.consent_given = True
        self.match_profile.visible = True
        self.match_profile.pending = False
        self.match_profile.is_beta_tester = True
        self.match_profile.phone = '0123456789'
        self.match_profile.photos = ['pic.jpg']
        self.match_profile.save()
        Swipe.objects.create(from_user=self.user, to_user=self.match, decision='like')
        Swipe.objects.create(from_user=self.match, to_user=self.user, decision='like')

    def _auth_request(self):
        request = self.factory.get('/api/matches/')
        request.user = self.user
        return self.view(request)

    def test_returns_mutual_like(self):
        response = self._auth_request()
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(len(payload['matches']), 1)
        m = payload['matches'][0]
        self.assertEqual(m['name'], 'M X')
        self.assertEqual(m['phone'], '0123456789')

    def test_no_matches_empty(self):
        Swipe.objects.filter(from_user=self.user, to_user=self.match).delete()
        response = self._auth_request()
        payload = json.loads(response.content)
        self.assertEqual(payload['matches'], [])
