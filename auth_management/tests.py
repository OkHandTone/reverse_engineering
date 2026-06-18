from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from business_management.models import Business

User = get_user_model()


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='login_user',
            password='pass12345',
            email='login@example.com',
            phone='0611111111',
            first_name='Login',
            last_name='User',
            identification_number='LOGIN001',
        )

    def test_login_returns_token_and_user(self):
        response = self.client.post(
            self.url,
            {'username': 'login_user', 'password': 'pass12345'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'login_user')
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_login_invalid_password_returns_401(self):
        response = self.client.post(
            self.url,
            {'username': 'login_user', 'password': 'wrong-password'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_unknown_user_returns_401(self):
        response = self.client.post(
            self.url,
            {'username': 'unknown_user', 'password': 'pass12345'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields_returns_400(self):
        response = self.client.post(self.url, {'username': 'login_user'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_returns_401(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        response = self.client.post(
            self.url,
            {'username': 'login_user', 'password': 'pass12345'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('my_profile')
        self.user = User.objects.create_user(
            username='profile_user',
            password='pass12345',
            email='profile@example.com',
            phone='0610101010',
            first_name='Profile',
            last_name='User',
            identification_number='PROFILE001',
        )

    def test_profile_returns_authenticated_user(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'profile_user')
        self.assertIn('token', response.data)

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProtectedRouteAccessTests(TestCase):
    """Vérifie que les routes protégées exigent un token valide."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='protected_user',
            password='pass12345',
            email='protected@example.com',
            phone='0612121212',
            first_name='Protected',
            last_name='User',
            identification_number='PROT001',
            user_type=User.UserType.CLIENT,
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)

        self.protected_routes = [
            ('GET', reverse('my_profile')),
            ('GET', reverse('get_business')),
            (
                'POST',
                reverse('register'),
                {
                    'username': 'new_user',
                    'password': 'pass12345',
                    'user_type': User.UserType.CLIENT,
                    'first_name': 'New',
                    'last_name': 'User',
                    'phone': '0699999999',
                    'identification_number': 'NEW001',
                },
            ),
        ]

    def test_protected_routes_reject_unauthenticated_requests(self):
        for route in self.protected_routes:
            method, url = route[0], route[1]

            with self.subTest(method=method, url=url):
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url, route[2], format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_routes_allow_authenticated_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        profile_response = self.client.get(reverse('my_profile'))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

        business_response = self.client.get(reverse('get_business'))
        self.assertEqual(business_response.status_code, status.HTTP_200_OK)

    def test_login_route_is_public(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'protected_user', 'password': 'pass12345'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

        self.client_owner = User.objects.create_user(
            username='client_owner',
            password='pass12345',
            email='owner@example.com',
            phone='0622222222',
            first_name='Owner',
            last_name='Client',
            identification_number='CLIENT001',
            user_type=User.UserType.CLIENT,
        )
        self.other_client = User.objects.create_user(
            username='other_client',
            password='pass12345',
            email='other@example.com',
            phone='0622222223',
            first_name='Other',
            last_name='Client',
            identification_number='CLIENT002',
            user_type=User.UserType.CLIENT,
        )
        self.worker = User.objects.create_user(
            username='worker_user',
            password='pass12345',
            email='worker@example.com',
            phone='0633333333',
            first_name='Worker',
            last_name='User',
            identification_number='WORKER001',
            user_type=User.UserType.WORKER,
            client=self.client_owner,
        )
        self.superadmin = User.objects.create_superuser(
            username='super_admin',
            password='pass12345',
            email='admin@example.com',
            phone='0644444444',
            first_name='Super',
            last_name='Admin',
            identification_number='ADMIN001',
        )
        self.business = Business.objects.create(name='Test Business', owner=self.client_owner)
        self.other_business = Business.objects.create(name='Other Business', owner=self.other_client)
        self.worker.business = self.business
        self.worker.save(update_fields=['business'])

    def _auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def _worker_payload(self, username, business=None):
        return {
            'username': username,
            'password': 'pass12345',
            'user_type': User.UserType.WORKER,
            'first_name': 'New',
            'last_name': 'Worker',
            'phone': '0655555555',
            'identification_number': username.upper(),
            'business': str((business or self.business).id),
        }

    def test_register_requires_authentication(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'anonymous',
                'password': 'pass12345',
                'user_type': User.UserType.CLIENT,
                'first_name': 'Anon',
                'last_name': 'User',
                'phone': '0699999998',
                'identification_number': 'ANON001',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_worker_cannot_register_users(self):
        self._auth_as(self.worker)
        response = self.client.post(
            self.register_url,
            self._worker_payload('blocked_worker'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Workers cannot register new users.')

    def test_client_can_only_register_workers(self):
        self._auth_as(self.client_owner)
        response = self.client.post(
            self.register_url,
            {
                'username': 'new_client',
                'password': 'pass12345',
                'user_type': User.UserType.CLIENT,
                'first_name': 'New',
                'last_name': 'Client',
                'phone': '0666666666',
                'identification_number': 'CLIENT003',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Clients can only register workers.')

    def test_client_registers_worker_with_forced_client(self):
        self._auth_as(self.client_owner)
        response = self.client.post(
            self.register_url,
            self._worker_payload('new_worker_ok'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(username='new_worker_ok')
        self.assertEqual(created.client_id, self.client_owner.id)
        self.assertEqual(created.user_type, User.UserType.WORKER)
        self.assertEqual(response.data['user']['client']['id'], self.client_owner.id)

    def test_client_cannot_register_worker_without_business(self):
        self._auth_as(self.client_owner)
        response = self.client.post(
            self.register_url,
            {
                'username': 'worker_no_business',
                'password': 'pass12345',
                'user_type': User.UserType.WORKER,
                'first_name': 'No',
                'last_name': 'Business',
                'phone': '0677777777',
                'identification_number': 'WORKER002',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_cannot_register_worker_with_foreign_business(self):
        self._auth_as(self.client_owner)
        response = self.client.post(
            self.register_url,
            self._worker_payload('worker_foreign_biz', business=self.other_business),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_superadmin_can_register_client(self):
        self._auth_as(self.superadmin)
        response = self.client.post(
            self.register_url,
            {
                'username': 'client_from_admin',
                'password': 'pass12345',
                'user_type': User.UserType.CLIENT,
                'first_name': 'From',
                'last_name': 'Admin',
                'phone': '0688888888',
                'identification_number': 'CLIENT004',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.get(username='client_from_admin').user_type,
            User.UserType.CLIENT,
        )

    def test_superadmin_can_register_worker_with_client_and_business(self):
        self._auth_as(self.superadmin)
        response = self.client.post(
            self.register_url,
            {
                **self._worker_payload('worker_from_admin'),
                'client': self.client_owner.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(username='worker_from_admin')
        self.assertEqual(created.user_type, User.UserType.WORKER)
        self.assertEqual(created.client_id, self.client_owner.id)

    def test_successful_register_returns_token_and_user(self):
        self._auth_as(self.superadmin)
        response = self.client.post(
            self.register_url,
            {
                'username': 'token_user',
                'password': 'pass12345',
                'user_type': User.UserType.CLIENT,
                'first_name': 'Token',
                'last_name': 'User',
                'phone': '0699999991',
                'identification_number': 'TOKEN001',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'token_user')
