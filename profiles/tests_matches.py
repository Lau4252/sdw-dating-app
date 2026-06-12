from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Profile, Swipe

class MatchesViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', password='test', first_name='Alice', last_name='Test', email='alice@test.de'
        )
        self.user.profile.consent_given = True
        self.user.profile.pending = False
        self.user.profile.visible = True
        self.user.profile.is_beta_tester = True
        self.user.profile.phone = '+491****6789'
        self.user.profile.save()

        self.bob = User.objects.create_user(
            username='bob', password='test', first_name='Bob', last_name='Test', email='bob@test.de'
        )
        self.bob.profile.consent_given = True
        self.bob.profile.pending = False
        self.bob.profile.visible = True
        self.bob.profile.is_beta_tester = True
        self.bob.profile.phone = '+499****4321'
        self.bob.profile.photos = ['/media/test.jpg']
        self.bob.profile.save()

    def test_no_matches_empty(self):
        self.client.force_login(self.user)
        resp = self.client.get('/profiles/matches/')
        print('Status:', resp.status_code)
        if resp.status_code == 302:
            print('Redirect to:', resp.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Noch keine Matches')

    def test_match_shows_phone(self):
        Swipe.objects.create(from_user=self.user, to_user=self.bob, decision='like')
        Swipe.objects.create(from_user=self.bob, to_user=self.user, decision='like')
        self.client.force_login(self.user)
        resp = self.client.get('/profiles/matches/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Bob Test')
        self.assertContains(resp, '+499****4321')
        self.assertContains(resp, 'Meine Matches')

    def test_match_card_has_photo(self):
        Swipe.objects.create(from_user=self.user, to_user=self.bob, decision='like')
        Swipe.objects.create(from_user=self.bob, to_user=self.user, decision='like')
        self.client.force_login(self.user)
        resp = self.client.get('/profiles/matches/')
        self.assertContains(resp, '/media/test.jpg')

    def test_non_mutual_not_shown(self):
        Swipe.objects.create(from_user=self.user, to_user=self.bob, decision='like')
        self.client.force_login(self.user)
        resp = self.client.get('/profiles/matches/')
        self.assertContains(resp, 'Noch keine Matches')
