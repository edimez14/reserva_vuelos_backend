from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.reservations.models import Reservation, Passenger


User = get_user_model()


class ReservationTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='reserva@correo.com',
			name='Usuario Reserva',
			phone='3222222222',
			password='PasswordSeguro123!'
		)
		token = RefreshToken.for_user(self.user).access_token
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

	def test_create_reservation_multiple_passengers(self):
		payload = {
			'flight_data': {
				'flight_number': 'LA901',
				'airline': 'LATAM',
				'origin': 'Bogotá',
				'destination': 'Cartagena',
				'departure_time': '2026-04-10T09:00:00Z',
				'arrival_time': '2026-04-10T10:30:00Z',
				'price': '320.00'
			},
			'passengers': [
				{'name': 'Ana Ruiz', 'document': '1000001', 'seat': '8A'},
				{'name': 'Luis Ruiz', 'document': '1000002', 'seat': '8B'}
			],
			'seat_selection': '8A,8B'
		}

		response = self.client.post('/api/v1/reservations', payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Reservation.objects.count(), 1)
		self.assertEqual(Passenger.objects.count(), 2)
		self.assertEqual(response.data['status'], 'pending')

	def test_get_user_reservations(self):
		self.test_create_reservation_multiple_passengers()

		response = self.client.get('/api/v1/reservations/user')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
