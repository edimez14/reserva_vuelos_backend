from django.utils import timezone
from django.contrib.auth import logout
from django.core.cache import cache
from django.http import JsonResponse
import hashlib

# Resumen:
# Este middleware revisa inactividad cuando el usuario está en flujo de compra.
# Si pasa mucho tiempo, limpia sesión para evitar compras "abiertas" por accidente.
class PurchaseTimeoutMiddleware:
    def __init__(self, get_response):
        # Django nos entrega la siguiente capa para continuar el flujo.
        self.get_response = get_response

    def __call__(self, request):
        # Aquí se ejecuta en cada request antes de llegar a la vista.
        # Solo aplicar en rutas de compra.
        is_purchase_path = request.path.startswith('/tickets/purchase') or request.path.startswith('/api/v1/purchase')
        if is_purchase_path:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            bearer_token = ''
            if auth_header.startswith('Bearer '):
                bearer_token = auth_header.split(' ', 1)[1].strip()

            # Si hay JWT, controlamos inactividad por token (válido para APIs con JWT).
            if bearer_token:
                token_hash = hashlib.sha256(bearer_token.encode('utf-8')).hexdigest()
                token_key = f'purchase_last_activity:{token_hash}'
                last_activity = cache.get(token_key)
                now = timezone.now().timestamp()

                if last_activity and (now - last_activity) > 900:
                    cache.delete(token_key)
                    return JsonResponse(
                        {'detail': 'Sesión expirada por inactividad durante compra.'},
                        status=401
                    )

                cache.set(token_key, now, timeout=900)
                response = self.get_response(request)
                return response

            # Fallback de sesión (si no usa JWT y sí usa sesión tradicional).
            if request.user.is_authenticated:
                last_activity = request.session.get('last_activity')
                now = timezone.now().timestamp()
                if last_activity and (now - last_activity) > 900:  # 15 minutos
                    logout(request)
                    request.session.flush()
                else:
                    # Si sigue activo, actualizamos la marca de última actividad.
                    request.session['last_activity'] = now

        response = self.get_response(request)
        return response