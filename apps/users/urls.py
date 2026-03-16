from django.urls import path
from .views import ProfileView, RegisterView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView

# Resumen:
# Mapa de endpoints de autenticación y perfil.
urlpatterns = [
    # Crea cuenta nueva.
    path('register', RegisterView.as_view(), name='register'),
    # Inicia sesión y devuelve JWT.
    path('login', LoginView.as_view(), name='login'),
    # Cierre de sesión lógico del lado cliente.
    path('logout', LogoutView.as_view(), name='logout'),
    # Solicita email de recuperación.
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
    # Confirma cambio de contraseña.
    path('reset-password', ResetPasswordView.as_view(), name='reset-password'),
    # Ver/editar/eliminar (soft delete) perfil propio.
    path('profile', ProfileView.as_view(), name='profile'),
]