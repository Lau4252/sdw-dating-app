# tests for browse, detail, matches views (tasks 3.1-3.3)
from django.test import TestCase, Client
from django.contrib.auth.models import User
from profiles.models import Profile, Swipe

class BrowseViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user('a@x.de', 'a@x.de', 'pw')
        self.u2 = User.objects.create_user('b@x.de', 'b@x.de', 'pw')
        self.p1 = self.u1.profile
        self.p1.visible = True; self.p1.pending = False; self.p1.consent_given = True; self.p1.is_beta_tester = True
        self.p1.hochschule = 'LMU'; self.p1.studienfach = 'BWL'
        self.p1.save()
        self.p2 = self.u2.profile
        self.p2.visible = True; self.p2.pending = False; self.p2.consent_given = True; self.p2.is_beta_tester = True
        self.p2.hochschule = 'TUM'; self.p2.studienfach = 'Informatik'
        self.p2.save()

    def test_browse_redirects_when_not_logged_in(self):
        resp = self.client.get('/browse/')
        self.assertEqual(resp.status_code, 302)

    def test_browse_shows_profiles_when_logged_in(self):
        self.client.force_login(self.u1)
        resp = self.client.get('/browse/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'LMU')
        self.assertContains(resp, 'TUM')

    def test_browse_filter_hochschule(self):
        self.client.force_login(self.u1)
        resp = self.client.get('/browse/?hochschule=LMU')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '0 Profile gefunden')
        # LMU should appear as selected option in the filterbar
        self.assertContains(resp, 'LMU')
        # The profile of u2 (TUM) should not appear in the results list
        self.assertNotContains(resp, 'b@x.de')
        self.assertContains(resp, 'Keine Profile gefunden')

    def test_my_matches_empty(self):
        self.client.force_login(self.u1)
        resp = self.client.get('/my-matches/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Noch keine Matches')

    def test_detail_view(self):
        self.client.force_login(self.u1)
        resp = self.client.get(f'/profiles/{self.p2.pk}/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'TUM')

    def test_detail_interest_button(self):
        self.client.force_login(self.u1)
        resp = self.client.get(f'/profiles/{self.p2.pk}/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Interesse zeigen')

    def test_detail_shows_match(self):
        Swipe.objects.create(from_user=self.u1, to_user=self.u2, decision='like')
        Swipe.objects.create(from_user=self.u2, to_user=self.u1, decision='like')
        self.client.force_login(self.u1)
        resp = self.client.get(f'/profiles/{self.p2.pk}/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "It's a Match")

    def test_swipe_api_like(self):
        import json
        self.client.force_login(self.u1)
        resp = self.client.post('/profiles/api/swipe/action/',
            data=json.dumps({'to_user_id': self.u2.id, 'decision': 'like'}),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        # No match yet because u2 hasn't liked u1
        self.assertFalse(data['match'])

    def test_swipe_api_match(self):
        import json
        Swipe.objects.create(from_user=self.u2, to_user=self.u1, decision='like')
        self.client.force_login(self.u1)
        resp = self.client.post('/profiles/api/swipe/action/',
            data=json.dumps({'to_user_id': self.u2.id, 'decision': 'like'}),
            content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['match'])

    def test_my_matches_with_match(self):
        Swipe.objects.create(from_user=self.u1, to_user=self.u2, decision='like')
        Swipe.objects.create(from_user=self.u2, to_user=self.u1, decision='like')
        self.client.force_login(self.u1)
        resp = self.client.get('/my-matches/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.u2.email)
