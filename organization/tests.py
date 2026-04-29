from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from client.models import Client
from employee.models import Employee
from service.models import Service

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


class OrganizationPanelAccessTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="root",
            email="root@example.com",
            password="pass1234",
        )
        self.regular_user = User.objects.create_user(username="regular", password="pass1234")
        admin_group, _ = Group.objects.get_or_create(name="admin")
        self.regular_user.groups.add(admin_group)
        self.organization = Organization.objects.create(name="Org Uno", slug="org-uno")
        UserProfile.objects.create(user=self.regular_user, organization=self.organization)

    def test_organization_list_redirects_anonymous_to_login(self):
        response = self.client.get(reverse('organization_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_organization_list_denies_non_superuser(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('organization_list'))
        self.assertEqual(response.status_code, 403)

    def test_organization_list_allows_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('organization_list'))
        self.assertEqual(response.status_code, 200)


class OrganizationPanelViewTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="root",
            email="root@example.com",
            password="pass1234",
        )
        self.client.force_login(self.superuser)

        self.organization = Organization.objects.create(name="Org Uno", slug="org-uno")
        self.other_organization = Organization.objects.create(name="Org Dos", slug="org-dos")

        self.member = User.objects.create_user(username="member", password="pass1234")
        UserProfile.objects.create(user=self.member, organization=self.organization)
        self.free_user = User.objects.create_user(username="free-user", password="pass1234")
        self.taken_user = User.objects.create_user(username="taken-user", password="pass1234")
        UserProfile.objects.create(user=self.taken_user, organization=self.other_organization)

        self.client_obj = Client.objects.create(first_name="Cliente", organization=self.organization)
        self.employee = Employee.objects.create(
            first_name="Empleado",
            last_name="Uno",
            phone_number="5551231234",
            organization=self.organization,
        )
        Service.objects.create(
            organization=self.organization,
            client=self.client_obj,
            service_title="Creado",
            service_number=1,
            status=Service.Status.Creating,
        )
        Service.objects.create(
            organization=self.organization,
            client=self.client_obj,
            service_title="Asignado",
            service_number=2,
            status=Service.Status.Assigned,
        )
        Service.objects.create(
            organization=self.organization,
            client=self.client_obj,
            service_title="Finalizado",
            service_number=3,
            status=Service.Status.Cancelled,
        )

    def test_organization_list_shows_organizations(self):
        response = self.client.get(reverse('organization_list'))
        self.assertContains(response, 'Org Uno')
        self.assertContains(response, 'Org Dos')

    def test_organization_create_generates_unique_slug(self):
        response = self.client.post(reverse('organization_create'), {'name': 'Org Uno'})
        self.assertEqual(response.status_code, 302)
        new_org = Organization.objects.exclude(pk=self.organization.pk).get(name='Org Uno')
        self.assertEqual(new_org.slug, 'org-uno-1')

    def test_organization_edit_page_loads(self):
        response = self.client.get(reverse('organization_edit', args=[self.organization.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar organización')
        self.assertContains(response, self.organization.slug)

    def test_organization_edit_updates_name_and_keeps_slug(self):
        response = self.client.post(
            reverse('organization_edit', args=[self.organization.slug]),
            {'name': 'Org Uno Editada'},
        )
        self.assertEqual(response.status_code, 302)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, 'Org Uno Editada')
        self.assertEqual(self.organization.slug, 'org-uno')

    def test_organization_detail_shows_operational_stats(self):
        response = self.client.get(reverse('organization_detail', args=[self.organization.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['total_services'], 3)
        self.assertEqual(response.context['stats']['active_assigned_services'], 1)
        self.assertEqual(response.context['stats']['finished_services'], 1)
        self.assertEqual(response.context['stats']['employees_count'], 1)
        self.assertEqual(response.context['stats']['clients_count'], 1)

    def test_organization_toggle_switches_active_flag(self):
        response = self.client.post(reverse('organization_toggle', args=[self.organization.slug]))
        self.assertEqual(response.status_code, 302)
        self.organization.refresh_from_db()
        self.assertFalse(self.organization.is_active)

    def test_organization_assign_user_creates_profile_for_free_user(self):
        response = self.client.post(
            reverse('organization_assign_user', args=[self.organization.slug]),
            {'user': self.free_user.pk},
        )
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.free_user)
        self.assertEqual(profile.organization, self.organization)

    def test_organization_assign_user_rejects_taken_user(self):
        response = self.client.post(
            reverse('organization_assign_user', args=[self.organization.slug]),
            {'user': self.taken_user.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.taken_user.refresh_from_db()
        self.assertEqual(self.taken_user.profile.organization, self.other_organization)

    def test_assign_user_form_only_lists_users_without_profile(self):
        response = self.client.get(reverse('organization_detail', args=[self.organization.slug]))
        form = response.context['assign_user_form']
        queryset_ids = set(form.fields['user'].queryset.values_list('id', flat=True))
        self.assertIn(self.free_user.id, queryset_ids)
        self.assertNotIn(self.member.id, queryset_ids)
        self.assertNotIn(self.taken_user.id, queryset_ids)


class OrganizationFormBehaviorTest(TestCase):
    def test_slugify_reference_behavior(self):
        self.assertEqual(slugify('Mi Organización Nueva'), 'mi-organizacion-nueva')
