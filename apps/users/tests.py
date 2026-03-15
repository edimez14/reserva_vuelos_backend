from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthenticationTests(APITestCase):
	def test_register_user_success(self):
		payload = {
			'email': 'nuevo@correo.com',
			'name': 'Usuario Nuevo',
			'phone': '3000000000',
			'password': 'PasswordSeguro123!',
			'password2': 'PasswordSeguro123!'
		}

		response = self.client.post('/api/v1/auth/register', payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('access', response.data)
		self.assertIn('refresh', response.data)
		self.assertEqual(User.objects.count(), 1)

		user = User.objects.get(email='nuevo@correo.com')
		self.assertTrue(user.check_password('PasswordSeguro123!'))

	def test_login_success(self):
		User.objects.create_user(
			email='login@correo.com',
			name='Usuario Login',
			phone='3111111111',
			password='PasswordSeguro123!'
		)

		payload = {
			'email': 'login@correo.com',
			'password': 'PasswordSeguro123!'
		}

		response = self.client.post('/api/v1/auth/login', payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('access', response.data)
		self.assertIn('refresh', response.data)
