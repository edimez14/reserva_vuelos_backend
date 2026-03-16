from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Resumen:
# Este archivo define el usuario personalizado del sistema (login por email).
# También tiene el manager para crear usuarios y un "soft delete" para desactivar sin borrar físico.
class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User (autenticación con email)."""
    def create_user(self, email, password=None, **extra_fields):
        # Validamos email porque es el identificador principal de login.
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado de usuario.
    - Se autentica con email (username no se usa).
    - Incluye soft delete mediante campo deleted_at.
    """
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    name = models.CharField(max_length=150, verbose_name='Nombre completo')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')

    # Campos requeridos por Django para administración
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # campos adicionales al crear superusuario

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    def soft_delete(self):
        # En vez de borrar el registro, lo marcamos como inactivo.
        """Marca el usuario como eliminado (soft delete)."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()