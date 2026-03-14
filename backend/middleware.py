from django.utils import timezone
from django.contrib.auth import logout

# Resumen:
# Este middleware revisa inactividad cuando el usuario está en flujo de compra.
# Si pasa mucho tiempo, limpia sesión para evitar compras "abiertas" por accidente.
class PurchaseTimeoutMiddleware:
    def __init__(self, get_response):
        # Django nos entrega la siguiente capa para continuar el flujo.
        self.get_response = get_response

    def __call__(self, request):
        # Aquí se ejecuta en cada request antes de llegar a la vista.
        # Solo aplicar si el usuario está autenticado y la ruta es de compra
        if request.user.is_authenticated and request.path.startswith('/tickets/purchase'):
            last_activity = request.session.get('last_activity')
            now = timezone.now().timestamp()
            if last_activity and (now - last_activity) > 900:  # 15 minutos
                # Si se pasó el tiempo, cerramos sesión y limpiamos datos de sesión.
                logout(request)
                # Puedes redirigir o devolver error, pero como es API, mejor devolver 401
                # Sin embargo, aquí no podemos modificar la respuesta, lo haremos en la vista
                # En su lugar, podemos marcar la sesión como expirada y luego en la vista chequear
                request.session.flush()
            else:
                # Si sigue activo, actualizamos la marca de última actividad.
                request.session['last_activity'] = now
        response = self.get_response(request)
        return response