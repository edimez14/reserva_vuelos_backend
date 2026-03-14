# documentacion de reserva vuelos backend

## feature/5-reservations

En esta rama se implementó el sistema de reservas. Ahora los usuarios autenticados pueden reservar vuelos (los que vienen de la API externa) para uno o múltiples pasajeros, con selección opcional de asiento.

### Endpoints creados

| Método | Endpoint               | Descripción                          | Autenticación |
|--------|------------------------|--------------------------------------|---------------|
| POST   | /reservations          | Crea una nueva reserva               | Requiere JWT  |
| GET    | /reservations/user     | Lista todas las reservas del usuario | Requiere JWT  |

### Formato de datos

**POST /reservations** (ejemplo de body):

```json
{
  "flight_data": {
    "flight_number": "AV123",
    "airline": "Avianca",
    "origin": "Bogotá",
    "destination": "Medellín",
    "departure_time": "2026-03-20T10:00:00Z",
    "arrival_time": "2026-03-20T11:00:00Z",
    "price": 250
  },
  "passengers": [
    {
      "name": "Juan Pérez",
      "document": "12345678",
      "seat": "12A"
    },
    {
      "name": "María Gómez",
      "document": "87654321",
      "seat": "12B"
    }
  ],
  "seat_selection": "12A,12B"
}
```

**Respuesta (201 Created)**:

```json
{
  "id": 1,
  "flight": "AV123 - Bogotá → Medellín",
  "passengers_count": 2,
  "seat_selection": "12A,12B",
  "status": "pending",
  "created_at": "2026-03-13T20:30:00Z"
}
```

### Flujo de reserva

1. El usuario busca vuelos (fase 4) y selecciona uno.
2. El frontend envía los datos del vuelo (flight_data) más los pasajeros al backend.
3. El backend:
   - Busca el vuelo en la tabla `flights_flight` por número y fecha.
   - Si no existe, lo crea automáticamente con los datos proporcionados.
   - Crea la reserva con estado `pending`.
   - Crea los registros de pasajeros asociados.
4. Devuelve los datos de la reserva creada.

### Estados de reserva

- `pending`: recién creada, aún no pagada.
- `confirmed`: reserva pagada (se usará en fase 6).
- `cancelled`: reserva cancelada.

### Notas

- El campo `seat_selection` es opcional y puede ser un texto libre (ej: "12A,12B" o "ventana").
- Se soportan múltiples pasajeros en una misma reserva.
- El vuelo se guarda en la base de datos en el momento de la primera reserva. Así queda persistido para futuras consultas y relaciones.
- Todos los endpoints requieren token JWT en el header `Authorization`.