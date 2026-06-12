"""Tests for Swipe model and API endpoints."""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from profiles.models import Profile, Swipe

class SwipeAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.me = User.objects.create_user('me_test', email='me@example.com', password='testpass')
        self.them = User.objects.create_user('them_test', email='them@example.com', password='testpass')
        self.other = User.objects.create_user('other_test', email='other@example.com', password='testpass')

        for u in [self.me, self.them, self.other]:
            p = u.profile
            p.consent_given = True
            p.visible = True
            p.pending = False
            p.is_beta_tester = True
            p.gender = 'F'
            p.seeking = 'M'
            p.save()

        self.me.profile.gender = 'M'
        self.me.profile.seeking = 'F'
        self.me.profile.save()

    def test_swipe_next_returns_profile(self):
        self.client.force_login(self.me)
        resp = self.client.get('/profiles/api/swipe/next/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('id', data)

    def test_swipe_next_excludes_already_swiped(self):
        Swipe.objects.create(from_user=self.me, to_user=self.them, decision='pass')
        self.client.force_login(self.me)
        resp = self.client.get('/profiles/api/swipe/next/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['id'], self.other.id)

    def test_swipe_action_like_creates_record(self):
        self.client.force_login(self.me)
        resp = self.client.post(
            '/profiles/api/swipe/action/',
            data={'to_user_id': self.them.id, 'decision': 'like'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['match'])
        self.assertTrue(Swipe.objects.filter(from_user=self.me, to_user=self.them, decision='like').exists())

    def test_swipe_action_mutual_like_creates_match(self):
        Swipe.objects.create(from_user=self.them, to_user=self.me, decision='like')
        self.client.force_login(self.me)
        resp = self.client.post(
            '/profiles/api/swipe/action/',
            data={'to_user_id': self.them.id, 'decision': 'like'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['match'])
        self.assertIn('match_data', data)

    def test_swipe_action_pass(self):
        self.client.force_login(self.me)
        resp = self.client.post(
            '/profiles/api/swipe/action/',
            data={'to_user_id': self.them.id, 'decision': 'pass'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['match'])

    def test_match_list(self):
        Swipe.objects.create(from_user=self.me, to_user=self.them, decision='like')
        Swipe.objects.create(from_user=self.them, to_user=self.me, decision='like')
        self.client.force_login(self.me)
        resp = self.client.get('/profiles/api/matches/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['matches']), 1)
        self.assertEqual(data['matches'][0]['id'], self.them.id)

    def test_swipe_next_requires_consent(self):
        self.me.profile.consent_given = False
        self.me.profile.save()
        self.client.force_login(self.me)
        resp = self.client.get('/profiles/api/swipe/next/')
        self.assertEqual(resp.status_code, 403)

    def test_swipe_action_invalid_decision(self):
        self.client.force_login(self.me)
        resp = self.client.post(
            '/profiles/api/swipe/action/',
            data={'to_user_id': self.them.id, 'decision': 'invalid'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
