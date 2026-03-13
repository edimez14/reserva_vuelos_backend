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