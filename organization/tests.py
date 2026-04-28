from django.test import TestCase
from django.contrib.auth.models import User

from .models import Organization, UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_create_user_profile(self):
        profile = UserProfile.objects.create(user=self.user, organization=self.org)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.organization, self.org)

    def test_str_representation(self):
        profile = UserProfile.objects.create(user=self.user, organization=self.org)
        self.assertEqual(str(profile), "testuser — Test Org")

    def test_one_user_one_profile(self):
        UserProfile.objects.create(user=self.user, organization=self.org)
        with self.assertRaises(Exception):
            UserProfile.objects.create(user=self.user, organization=self.org)

    def test_cascade_on_org_delete(self):
        UserProfile.objects.create(user=self.user, organization=self.org)
        self.org.delete()
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 0)
