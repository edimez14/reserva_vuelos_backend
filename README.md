# documentacion de reserva vuelos backend

## feature/fix-append-slash

En esta rama se corrigió un error del servidor que hacía que el endpoint `POST /api/v1/reservations` devolviera un error 500.

### El problema

Django tiene una configuración que se llama `APPEND_SLASH`. Por defecto está activada y lo que hace es: si alguien llama a una URL sin barra al final (como `/reservations`), Django intenta redirigirla a la versión con barra (`/reservations/`). Eso funciona bien para peticiones GET, pero cuando la petición es POST (como al crear una reserva), Django no puede hacer esa redirección porque perdería los datos del formulario. Entonces lanza un error 500.

```
RuntimeError: You called this URL via POST, but the URL doesn't end in a slash
and you have APPEND_SLASH set.
```

### La solución

Se hicieron tres cambios:

**1. `backend/settings.py`**

Se agregó `APPEND_SLASH = False`. Esto le dice a Django que no intente redirigir URLs cuando les falta la barra final. Así la URL llega directamente al view sin problema.

```python
# Sin esto, Django intenta redirigir POST /reservations → /reservations/ y explota.
# Con False, Django no agrega la barra final automáticamente.
APPEND_SLASH = False
```

**2. `backend/urls.py`**

Se cambiaron las rutas de reservas y compra de `include()` a rutas directas. Esto es porque cuando el prefijo no tiene barra final y se usa `include()`, Django no puede resolver bien las sub-rutas (por ejemplo `/reservations/user`). Al declarar las rutas directamente se evita ese problema.

```python
# Antes (causaba el problema):
path('api/v1/reservations/', include('apps.reservations.urls')),
path('api/v1/tickets/', include('apps.tickets.urls')),

# Después (correcto):
path('api/v1/reservations', ReservationCreateView.as_view(), name='reservation-create'),
path('api/v1/reservations/user', UserReservationsView.as_view(), name='user-reservations'),
path('api/v1/purchase', PurchaseView.as_view(), name='purchase'),
```

**3. `apps/tickets/urls.py`**

Se actualizó el path interno de la compra para que coincida con la nueva ruta directa.

### Cómo verificar que funciona

```bash
python manage.py check  # Debe decir: System check identified no issues
```

```bash
python manage.py shell -c "
from django.urls import resolve
print(resolve('/api/v1/reservations').func.view_class.__name__)
print(resolve('/api/v1/reservations/user').func.view_class.__name__)
print(resolve('/api/v1/purchase').func.view_class.__name__)
"
# Debe imprimir:
# ReservationCreateView
# UserReservationsView
# PurchaseView
```

