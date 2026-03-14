# documentacion de reserva vuelos backend

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