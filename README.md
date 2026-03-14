# documentacion de reserva vuelos backend

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