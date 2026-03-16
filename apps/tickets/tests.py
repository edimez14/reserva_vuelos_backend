from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
import hashlib
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.flights.models import Flight
from apps.reservations.models import Reservation
from apps.tickets.models import Ticket


User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PurchaseTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='compra@correo.com',
			name='Usuario Compra',
			phone='3333333333',
			password='PasswordSeguro123!'
		)
		self.flight = Flight.objects.create(
			flight_number='AV555',
			airline='Avianca',
			origin='Bogotá',
			destination='Cali',
			departure_time='2026-05-10T08:00:00Z',
			arrival_time='2026-05-10T09:00:00Z',
			price='280.00',
			seats_available=100,
		)
		self.reservation = Reservation.objects.create(
			user=self.user,
			flight=self.flight,
			passengers_count=1,
			seat_selection='4A',
			status='pending'
		)
		access_token = str(RefreshToken.for_user(self.user).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		self.access_token = access_token

	def test_purchase_success(self):
		payload = {
			'reservation_id': self.reservation.id,
			'payment_method': 'visa'
		}

		response = self.client.post('/api/v1/purchase', payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Ticket.objects.count(), 1)

		self.reservation.refresh_from_db()
		self.assertEqual(self.reservation.status, 'confirmed')

	def test_purchase_timeout_inactivity(self):
		token_hash = hashlib.sha256(self.access_token.encode('utf-8')).hexdigest()
		cache_key = f'purchase_last_activity:{token_hash}'
		expired_timestamp = 1
		cache.set(cache_key, expired_timestamp, timeout=900)

		payload = {
			'reservation_id': self.reservation.id,
			'payment_method': 'visa'
		}
		response = self.client.post('/api/v1/purchase', payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertIn('detail', response.json())
		self.assertEqual(Ticket.objects.count(), 0)
