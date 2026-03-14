# documentacion de reserva vuelos backend

## rama dev

### rama feature/1-backend-setup

En esta rama se creo la estructura del proyecto

las apps que usara el backend son las siguientes:
- users (apps para el registro y login de los usuarios)
- flights (datos y consultas de los vuelos y mostrar los vuelos de la api externa)
- reservations (reservacion de vuelos, control de compras)
- tickets (generacion de ticketes de compra)
- emails (envio de emails)

Tambien se crearon los archivos de .env, y se realizo  la conexion a la base de datos de forma remota usando neon console

Tiene el dockerfile para prepararlo para el despligue en fly

### rama feature/2-database-models

En esta rama se crearon los modelos de datos y se configuró la base de datos remota en **Neon (PostgreSQL)**. Se eligió Neon por su simplicidad y rapidez para entornos de desarrollo, permitiendo mantener la BD accesible desde cualquier lugar sin depender de una instancia local.

#### Modelos creados y relaciones

| App         | Modelo     | Relaciones                                                                 | Propósito                                                                 |
|-------------|------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `users`     | `User`     | No tiene relaciones foráneas directas, pero es referenciado por otros.    | Usuario personalizado con autenticación por email y soft delete.         |
| `flights`   | `Flight`   | Independiente, contiene datos de vuelos (pueden venir de API externa).    | Almacena información básica de vuelos: número, aerolínea, origen, destino, horarios, precio y asientos disponibles. |
| `reservations` | `Reservation` | `user` (ForeignKey a `User`), `flight` (ForeignKey a `Flight`)           | Representa una reserva hecha por un usuario sobre un vuelo específico.   |
| `reservations` | `Passenger` | `reservation` (ForeignKey a `Reservation`, relaciona varios pasajeros a una reserva) | Permite registrar múltiples pasajeros en una misma reserva, con opción de asiento. |
| `tickets`   | `Ticket`   | `reservation` (OneToOneField a `Reservation`)                             | Se genera al confirmar la compra, vinculando un boleto a una reserva única. |

#### ¿Por qué estas relaciones?

- **Reserva ↔ Usuario**: Un usuario puede tener muchas reservas, pero cada reserva pertenece a un solo usuario.
- **Reserva ↔ Vuelo**: Cada reserva es para un vuelo específico; así mantenemos consistencia en tarifas y disponibilidad.
- **Pasajero ↔ Reserva**: Soporta el requisito de reservar para múltiples pasajeros bajo un mismo itinerario.
- **Ticket ↔ Reserva**: Relación uno a uno porque una reserva pagada genera un único boleto (o conjunto de boletos ligados a los pasajeros). Aquí simplificamos: el ticket representa el comprobante de compra asociado a la reserva.

#### Migración a Neon

- Se configuró la base de datos en Neon y se actualizó `DATABASES` en `settings.py` con las credenciales de la instancia remota.
- Se ejecutaron las migraciones directamente sobre la BD en la nube:
  ```bash
  python manage.py makemigrations users flights reservations tickets
  python manage.py migrate
  ```
- Esto asegura que el equipo pueda trabajar siempre contra el mismo estado de base de datos, sin conflictos locales.

#### Nota adicional

- El modelo `User` utiliza `email` como identificador único (`USERNAME_FIELD`) y está configurado en `settings.py` con `AUTH_USER_MODEL = 'users.User'`.
- Se incluyó el campo `deleted_at` para soft delete en usuarios, cumpliendo el requisito de desactivación sin borrado físico.

### feature/3-authentication

En esta rama se implementó el sistema completo de autenticación usando JWT. Se crearon los endpoints necesarios para registro, inicio de sesión, cierre de sesión, recuperación de contraseña y restablecimiento de contraseña. Se utilizó Django REST Framework y SimpleJWT para los tokens.

#### Endpoints creados

| Método | Endpoint               | Descripción                          |
|--------|------------------------|--------------------------------------|
| POST   | /auth/register         | Registra un nuevo usuario            |
| POST   | /auth/login            | Inicia sesión y devuelve tokens JWT  |
| POST   | /auth/logout           | Cierra sesión (solo indica al cliente) |
| POST   | /auth/forgot-password  | Envía correo con link para reset     |
| POST   | /auth/reset-password   | Cambia la contraseña con token válido |

#### Flujo de autenticación

- **Registro**: El usuario envía email, nombre, teléfono y contraseña (dos veces). Si las contraseñas coinciden y son válidas, se crea el usuario (con password cifrado por Django) y se devuelven access y refresh tokens (queda logueado automáticamente).
- **Login**: Se envían email y contraseña. Si son correctos, se devuelven tokens y datos básicos del usuario.
- **Logout**: Simplemente responde OK; el cliente debe eliminar los tokens almacenados.
- **Recuperación de contraseña**: Se envía email al correo proporcionado. El email contiene un link con uid y token (generados por Django). En desarrollo, los emails se muestran en consola.
- **Restablecimiento de contraseña**: Se envía uid, token y nueva contraseña. Si el token es válido, se actualiza la contraseña.

#### Configuración de JWT

- Access token: 15 minutos de duración.
- Refresh token: 1 día de duración.

#### Seguridad

- Las contraseñas se cifran automáticamente con el hasher predeterminado de Django (PBKDF2).
- Los tokens JWT se utilizan para autenticación en endpoints protegidos.

#### Dependencias añadidas

- `djangorestframework-simplejwt`

#### Notas

- El envío de correos está configurado en modo consola (`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`), por lo que los correos se imprimen en la terminal donde corre el servidor.
- Para producción se deberá cambiar a un backend real (SMTP, SendGrid, etc.).

## feature/4-flight-api

En esta rama se integró una API externa de vuelos (AviationStack) para permitir búsquedas en tiempo real. Se creó un servicio que consume la API, se añadió el endpoint `/flights/search` y se implementaron filtros básicos.

### Endpoint creado

| Método | Endpoint               | Descripción                          | Autenticación |
|--------|------------------------|--------------------------------------|---------------|
| GET    | /flights/search        | Busca vuelos según parámetros        | Requiere JWT  |

### Parámetros de búsqueda

| Parámetro | Tipo    | Descripción                          | Ejemplo       |
|-----------|---------|--------------------------------------|---------------|
| origin    | string  | Código IATA del aeropuerto origen    | BOG           |
| destination| string | Código IATA del aeropuerto destino   | MDE           |
| date      | string  | Fecha del vuelo (YYYY-MM-DD)         | 2026-03-20    |
| airline   | string  | Nombre de la aerolínea (opcional)    | Avianca       |
| direct    | boolean | Solo vuelos directos (no implementado en API free) | true |

### Flujo de búsqueda

1. El cliente autenticado hace una petición GET al endpoint con los parámetros deseados.
2. El backend valida los parámetros con un serializer.
3. Se instancia el servicio `FlightAPIService` que consulta la API de AviationStack.
4. La respuesta de la API se transforma al formato interno de la aplicación (incluyendo precio simulado, ya que la API gratuita no proporciona tarifas reales).
5. Se devuelve un listado de vuelos con la información estandarizada.

### Dependencias añadidas

- `requests` (para llamadas HTTP a la API externa)
- `python-decouple` (para manejar variables de entorno, ya se usaba)

### Variables de entorno

Se debe agregar en el archivo `.env`:

```
AVIATIONSTACK_API_KEY=tu_api_key
```

### Notas

- La API gratuita de AviationStack tiene un límite de 100 peticiones por mes.
- Los precios son simulados con valores aleatorios entre 150 y 800 USD.
- El parámetro `direct` no se implementa porque la versión gratuita no lo soporta; se ignora.
- Solo usuarios autenticados pueden buscar vuelos (requiere token JWT en el header `Authorization`).

### Ejemplo de uso

```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/flights/search"
```

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

## feature/6-ticket-purchase

En esta rama se implementó el flujo de compra de boletos. Los usuarios pueden comprar una reserva previamente creada (simulación de pago con tarjeta de crédito). Al confirmar la compra, se genera un ticket, se actualiza el estado de la reserva a `confirmed` y se envía un email de confirmación (y otro con el billete). También se añadió un middleware que cierra la sesión tras 15 minutos de inactividad durante el proceso de compra.

### Endpoints creados

| Método | Endpoint               | Descripción                          | Autenticación |
|--------|------------------------|--------------------------------------|---------------|
| POST   | /tickets/purchase      | Procesa la compra de una reserva     | Requiere JWT  |

### Formato de datos

**POST /tickets/purchase** (ejemplo de body):

```json
{
  "reservation_id": 1,
  "payment_method": "visa"
}
```

**Respuesta (201 Created)**:

```json
{
  "message": "Compra exitosa",
  "ticket_id": 1,
  "reservation_id": 1
}
```

### Flujo de compra

1. El usuario (autenticado) selecciona una reserva en estado `pending`.
2. Envía una petición POST a `/tickets/purchase` con el ID de la reserva y método de pago simulado.
3. El backend valida que la reserva exista, pertenezca al usuario y esté pendiente.
4. Se crea un ticket con estado `paid` y se actualiza la reserva a `confirmed`.
5. Se envían dos correos electrónicos al usuario:
   - Confirmación de compra.
   - Billete electrónico (simulado en texto plano).
6. Se retorna la confirmación.

### Timeout de compra

Se implementó un middleware (`PurchaseTimeoutMiddleware`) que monitorea la actividad del usuario en rutas que comienzan con `/tickets/purchase`. Si pasan más de 15 minutos sin actividad, la sesión se destruye automáticamente, forzando al usuario a iniciar sesión nuevamente.

### Configuración de email

Para desarrollo, los correos se imprimen en consola con `EMAIL_BACKEND = 'console'`. Para producción, se debe configurar SMTP real en las variables de entorno.

## feature/email-system

En esta rama se implementó el sistema de envío de correos electrónicos para todas las notificaciones relevantes del sistema. Se creó una app dedicada `emails` con servicios reutilizables y se integró en los flujos de registro, recuperación de contraseña y compra.

### Funcionalidades de correo

| Tipo de correo               | Disparador                          | Destinatario       |
|------------------------------|-------------------------------------|--------------------|
| Confirmación de registro     | Registro de nuevo usuario           | Usuario registrado |
| Recuperación de contraseña   | Solicitud de olvido de contraseña   | Usuario solicitante |
| Confirmación de compra       | Compra exitosa de un ticket         | Usuario comprador  |
| Billete electrónico          | Compra exitosa de un ticket         | Usuario comprador  |

### Servicios implementados

En `apps/emails/services.py` se crearon las siguientes funciones:

- `send_registration_email(user_email, user_name)`
- `send_password_reset_email(user_email, reset_link)`
- `send_purchase_confirmation(user_email, ticket)`
- `send_ticket_receipt(user_email, ticket)`

Todas utilizan `django.core.mail.send_mail` con configuración centralizada.

### Configuración de email

En `settings.py` se definieron las siguientes variables (cargadas desde entorno):

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

Ahora vamos a usar el modo de smtp para que se puedan enviar email reales

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### Integración en vistas

- **Registro**: En `RegisterView`, después de crear el usuario, se llama a `send_registration_email`.
- **Olvido de contraseña**: En `ForgotPasswordSerializer.save()` se genera el enlace de restablecimiento y se llama a `send_password_reset_email`.
- **Compra**: En `PurchaseView`, después de crear el ticket, se llaman a `send_purchase_confirmation` y `send_ticket_receipt`.

### Variables de entorno necesarias

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_o_app_password
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
```

### Notas

- En desarrollo, los correos se muestran en la consola si se usa el backend de consola.
- En producción, se debe usar un servidor SMTP real (Gmail, SendGrid, etc.).
- Los correos son actualmente en texto plano; pueden mejorarse con HTML en el futuro.

## feature/7-profile-management

En esta rama se implementó la gestión del perfil de usuario. Los usuarios autenticados pueden ver su información, actualizar sus datos (nombre y teléfono) y desactivar su cuenta (soft delete).

### Endpoints creados

| Método | Endpoint    | Descripción                          | Autenticación |
|--------|-------------|--------------------------------------|---------------|
| GET    | /auth/profile | Obtiene los datos del perfil         | Requiere JWT  |
| PUT    | /auth/profile | Actualiza nombre y/o teléfono        | Requiere JWT  |
| DELETE | /auth/profile | Desactiva la cuenta (soft delete)    | Requiere JWT  |

### Formato de datos

**GET /auth/profile** (respuesta):

```json
{
  "id": 1,
  "email": "usuario@example.com",
  "name": "Juan Pérez",
  "phone": "3001234567",
  "created_at": "2026-03-13T20:30:00Z"
}
```

**PUT /auth/profile** (ejemplo de body, solo campos a modificar):

```json
{
  "name": "Juan Carlos Pérez",
  "phone": "3007654321"
}
```

**Respuesta** (200 OK): el perfil actualizado (mismos campos que GET).

**DELETE /auth/profile** (respuesta):

```json
{
  "detail": "Usuario desactivado correctamente."
}
```

### Flujo

- **GET**: Retorna los datos del usuario autenticado (campos: id, email, name, phone, created_at). El email no se puede modificar.
- **PUT**: Permite actualizar `name` y/o `phone` (parcialmente). El resto de campos son de solo lectura.
- **DELETE**: Ejecuta el método `soft_delete()` del modelo, que cambia `is_active` a `False` y asigna la fecha actual a `deleted_at`. El usuario ya no podrá iniciar sesión.

### Notas

- Todos los endpoints requieren token JWT en el header `Authorization`.
- El soft delete no borra físicamente al usuario, solo lo desactiva.
- Para reactivar un usuario, sería necesario un proceso administrativo (no implementado).