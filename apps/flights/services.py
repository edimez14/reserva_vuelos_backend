import requests
from django.conf import settings

class FlightAPIService:
    COLOMBIA_IATA = [
        'BOG', 'MDE', 'CTG', 'CLO', 'BAQ', 'SMR', 'BGA', 'PEI',
        'ADZ', 'CUC', 'RCH', 'AXM', 'MTR', 'EOH', 'LET'
    ]

    def __init__(self):
        self.api_key = (getattr(settings, 'AVIATIONSTACK_API_KEY', '') or '').strip()
        self.base_url = getattr(settings, 'AVIATIONSTACK_API_URL', 'http://api.aviationstack.com/v1/flights')
        
    def search_flights(self, origin=None, destination=None, date=None, airline=None, direct=None):
        if not self.api_key:
            return {'error': 'No se configuró AVIATIONSTACK_API_KEY en variables de entorno.'}

        params = {'access_key': self.api_key, 'limit': 20}
        restricted_mode = False
        colombia_mode = not origin and not destination

        if colombia_mode:
            params['limit'] = 100

        if origin:
            params['dep_iata'] = origin
        if destination:
            params['arr_iata'] = destination
        if date:
            params['flight_date'] = str(date)
        if airline:
            params['airline_name'] = airline

        try:
            if colombia_mode:
                all_data = []
                for iata in self.COLOMBIA_IATA:
                    page_params = {'access_key': self.api_key, 'limit': 10, 'dep_iata': iata}
                    if airline:
                        page_params['airline_name'] = airline

                    response = requests.get(self.base_url, params=page_params, timeout=10)
                    page_data = response.json()

                    if 'error' in page_data:
                        continue

                    all_data.extend(page_data.get('data', []))

                data = {'data': all_data}
            else:
                response = requests.get(self.base_url, params=params, timeout=10)
                data = response.json()

            if 'error' in data:
                if data['error'].get('code') == 'function_access_restricted':
                    restricted_mode = True
                    fallback_params = {'access_key': self.api_key, 'limit': 100}
                    if origin:
                        fallback_params['dep_iata'] = origin
                    if destination:
                        fallback_params['arr_iata'] = destination
                    if airline:
                        fallback_params['airline_name'] = airline
                    response = requests.get(self.base_url, params=fallback_params, timeout=10)
                    data = response.json()
                else:
                    detail = data['error'].get('message') or data['error'].get('info') or 'Error en API externa.'
                    return {'error': detail}

            if 'error' in data:
                detail = data['error'].get('message') or data['error'].get('info') or 'Error en API externa.'
                return {'error': detail}

            flights = []
            seen = set()
            for flight in data.get('data', []):
                if not (flight.get('departure') and flight.get('arrival') and flight.get('flight')):
                    continue

                departure = flight['departure']
                arrival = flight['arrival']
                flight_info = flight['flight']
                airline_info = flight.get('airline', {})

                flight_origin_iata = departure.get('iata', '')
                flight_destination_iata = arrival.get('iata', '')
                flight_date = flight.get('flight_date', '')

                if colombia_mode and not self._is_colombia_departure(departure):
                    continue

                if origin and flight_origin_iata != origin:
                    continue
                if destination and flight_destination_iata != destination:
                    continue
                if date and not restricted_mode and str(date) != flight_date:
                    continue

                flight_key = (
                    flight_info.get('iata') or flight_info.get('number') or '',
                    flight_origin_iata,
                    flight_destination_iata,
                    departure.get('scheduled') or ''
                )
                if flight_key in seen:
                    continue
                seen.add(flight_key)

                flights.append({
                    'flight_number': flight_info.get('iata') or flight_info.get('number') or 'N/A',
                    'airline': airline_info.get('name', 'Desconocida'),
                    'origin': departure.get('airport', ''),
                    'origin_iata': flight_origin_iata,
                    'destination': arrival.get('airport', ''),
                    'destination_iata': flight_destination_iata,
                    'departure_time': departure.get('scheduled'),
                    'arrival_time': arrival.get('scheduled'),
                    'status': flight.get('flight_status', 'unknown'),
                    'price': self._get_simulated_price(flight),
                    'seats_available': 150,
                })

            return {'flights': flights}
        except requests.RequestException as e:
            return {'error': str(e)}
    
    def _get_simulated_price(self, flight):
        from random import randint
        return randint(150, 800)

    def _is_colombia_departure(self, departure):
        icao = (departure.get('icao') or '').upper()
        timezone = (departure.get('timezone') or '').lower()
        country = (departure.get('country') or '').lower()
        return icao.startswith('SK') or 'america/bogota' in timezone or 'colombia' in country