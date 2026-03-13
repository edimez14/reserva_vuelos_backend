# documentacion de reserva vuelos backend

## rama dev

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