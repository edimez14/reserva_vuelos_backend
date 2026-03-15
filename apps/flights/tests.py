from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase


class FlightSearchTests(APITestCase):
	@patch('apps.flights.views.FlightAPIService.search_flights')
	def test_search_flights_success(self, mock_search):
		mock_search.return_value = {
			'flights': [
				{
					'flight_number': 'AV123',
					'airline': 'Avianca',
					'origin': 'Bogotá',
					'origin_iata': 'BOG',
					'destination': 'Medellín',
					'destination_iata': 'MDE',
					'departure_time': '2026-03-20T10:00:00Z',
					'arrival_time': '2026-03-20T11:00:00Z',
					'status': 'scheduled',
					'price': 250,
					'seats_available': 120,
				}
			]
		}

		response = self.client.get('/api/v1/flights/search')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['flight_number'], 'AV123')

	def test_search_flights_invalid_params(self):
		response = self.client.get('/api/v1/flights/search', {'date': 'no-fecha'})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
