from django.utils import timezone
from django.contrib.auth import logout

class PurchaseTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo aplicar si el usuario está autenticado y la ruta es de compra
        if request.user.is_authenticated and request.path.startswith('/tickets/purchase'):
            last_activity = request.session.get('last_activity')
            now = timezone.now().timestamp()
            if last_activity and (now - last_activity) > 900:  # 15 minutos
                logout(request)
                # Puedes redirigir o devolver error, pero como es API, mejor devolver 401
                # Sin embargo, aquí no podemos modificar la respuesta, lo haremos en la vista
                # En su lugar, podemos marcar la sesión como expirada y luego en la vista chequear
                request.session.flush()
            else:
                request.session['last_activity'] = now
        response = self.get_response(request)
        return response