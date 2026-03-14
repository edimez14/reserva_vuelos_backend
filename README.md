# documentacion de reserva vuelos backend

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