from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Profile

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.create(
            user=self.user,
            email='testuser@test.com',
            first_name='fill',
            last_name='colson'
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.email, 'testuser@test.com')
        self.assertEqual(self.profile.first_name, 'fill')
        self.assertEqual(self.profile.last_name, 'colson')

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'testuser-testuser@test.com')

    def test_fullname_property(self):
        self.assertEqual(self.profile.fullname, 'fill colson')

    def test_profile_ordering(self):
        user2 = User.objects.create_user(username='testuser2', password='testpassword')
        Profile.objects.create(
            user=user2,
            email='testuser2@test.com',
            first_name='ville',
            last_name='Smith'
        )

        # Retrieve all profiles and ensure they are ordered by ID in descending order
        profiles = Profile.objects.all()
        self.assertEqual(profiles[0].user.username, 'testuser2')
        self.assertEqual(profiles[1].user.username, 'testuser')

    def test_profile_blank_fields(self):
        user2 = User.objects.create_user(username='testuser2', password='testpassword')
        profile = Profile.objects.create(user=user2)
        self.assertEqual(profile.email, '')
        self.assertEqual(profile.first_name, '')
        self.assertEqual(profile.last_name, '')