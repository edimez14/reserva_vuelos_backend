from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ProfileSerializer
from apps.emails.services import send_registration_email

# Resumen:
# Este archivo tiene endpoints de autenticación y perfil.
# Flujo: registro/login -> tokens JWT -> acceso a endpoints protegidos.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Recibe datos, crea usuario y devuelve tokens para que el frontend inicie sesión.
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_registration_email(user.email, user.name)
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'name': user.name,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Valida credenciales y, si todo bien, emite JWT refresh/access.
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'email': user.email,
                        'name': user.name,
                    }
                })
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    # Simplemente requiere que el cliente elimine los tokens.
    def post(self, request):
        # Simplemente devolvemos OK
        return Response({'detail': 'Sesión cerrada. Elimina los tokens del cliente.'})

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Envía correo con enlace de recuperación.
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Se ha enviado un correo con instrucciones.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Cambia contraseña usando uid + token del correo.
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Contraseña actualizada correctamente.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retorna los datos del usuario autenticado.
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        # Actualización parcial del perfil (name, phone, etc.).
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Desactivación lógica del usuario (soft delete).
        request.user.soft_delete()
        return Response({'detail': 'Usuario desactivado correctamente.'}, status=status.HTTP_204_NO_CONTENT)