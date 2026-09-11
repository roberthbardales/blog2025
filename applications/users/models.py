from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
#
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    # TIPO DE USUARIOS
    ADMINISTRADOR = '0'
    USUARIO = '1'
    OTRO_USUARIO = '2'
    # GENEROS
    VARON = 'M'
    MUJER = 'F'
    OTRO_GENERO = 'O'
    #

    OCUPATION_CHOICES  = (
        (ADMINISTRADOR, 'Administrador'),
        (USUARIO, 'Usuario'),
        (OTRO_USUARIO, 'Otro'),
    )

    GENDER_CHOICES = (
        (VARON, 'Masculino'),
        (MUJER, 'Femenino'),
        (OTRO_GENERO, 'Otros'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField('Nombres', max_length=100)
    # ocupation = models.CharField(
    #     'Ocupacion',
    #     max_length=30,
    #     blank=True
    # )
    ocupation = models.CharField(
        max_length=1,
        choices=OCUPATION_CHOICES,
        blank=True
    )
    genero = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    date_birth = models.DateField(
        'Fecha de nacimiento',
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    #
    avatar_url = models.URLField(
        'URL Avatar Google',
        blank=True,
        null=True,
        help_text='URL de la imagen de Google'
    )
    #
    firebase_uid = models.CharField(max_length=255, blank=True, null=True, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

        # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name',]

    objects = UserManager()

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def __str__(self):
        return self.full_name or self.email