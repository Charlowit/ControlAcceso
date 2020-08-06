import hashlib

#from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
#from django.utils.encoding import python_2_unicode_compatible
from six import python_2_unicode_compatible
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

import uuid
from activatable_model.models import BaseActivatableModel
from django.conf import settings
import os
from django.templatetags.static import static

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from allauth.account.signals import user_signed_up

class MyUserManager(UserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

# Create your models here.
class CommonInfo(models.Model):
    created_at = models.DateTimeField(
        'Created at',
        auto_now_add=True,
        db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Created by',
        blank=True, null=True,
        related_name="%(app_label)s_%(class)s_created",
        on_delete=models.SET_NULL)
    lastmodified_at = models.DateTimeField(
        'Last modified at',
        auto_now=True,
        db_index=True)
    lastmodified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Last modified by',
        blank=True, null=True,
        related_name="%(app_label)s_%(class)s_lastmodified",
        on_delete=models.SET_NULL)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin, CommonInfo):
    """User instances represent a user on this site.

    Important: You don't have to use a custom user model. I did it here because
    I didn't want a username to be part of the system and I wanted other data
    to be part of the user and not in a separate table. 

    You can avoid the username issue without writing a custom model but it
    becomes increasingly obtuse as time goes on. Write a custom user model, then
    add a custom admin form and model.

    Remember to change ``AUTH_USER_MODEL`` in ``settings.py``.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email'), db_index=True, blank=False, unique=True)
    first_name = models.CharField(_('Nombre'), max_length=40, blank=True, null=True, unique=False)
    last_name = models.CharField(_('Apellidos'), max_length=40, blank=True, null=True, unique=False)
    display_name = models.CharField(_('Nombre a mostrar'), max_length=14, blank=True, null=True, unique=False)
    phone = models.CharField(_('Teléfono'), max_length=100, blank=False, null=False)
    dni = models.CharField(_('DNi'), max_length=10, blank=False, null=False)
    android = models.BooleanField(blank=True, default=False)
    ios = models.NullBooleanField(blank=True, default=False, null=True)
    acceptPush = models.BooleanField(_('Acepta Notificaciones'), default=False, blank=True, null=True)
    pushToken = models.CharField(max_length=100, null=True, blank=True,db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('Activo'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('Fecha de registro'), default=timezone.now)
    valid = models.BooleanField(default=True)
    is_business = models.BooleanField(_('Es una empresa?'), default=False, blank=True, null=True,
                                      help_text=_('Indica cuando el usuario es representante de uno o más negocios.'))

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'dni']
    class Meta:
        verbose_name = ('User')
        verbose_name_plural = ('Users')

    def get_absolute_url(self):
        # TODO: what is this for?
        return "/users/%s/" % urlquote(self.id)  # TODO: email ok for this? better to have uuid?
    def get_frontDNI_url(self):
        print (self.id)
        # Calculamos el path de las imágenes del usuario
        dnifront = os.path.join(settings.PROFILEMEDIA_BASE, str(self.id), settings.DNIFRONT)
        # comprobamos si existe el fichero
        if os.path.exists(os.path.join(settings.PROFILEMEDIA_ROOT, str(self.id), settings.DNIFRONT)):
            # Y las rutas estáticas
            return static(dnifront)
        else:
            return ''

    def get_backDNI_url(self):
        # Calculamos el path de las imágenes del usuario
        dniback = os.path.join(settings.PROFILEMEDIA_BASE, str(self.id), settings.DNIBACK)
        # comprobamos si existe el fichero
        if os.path.exists(os.path.join(settings.PROFILEMEDIA_ROOT, str(self.id), settings.DNIBACK)):
            # Y las rutas estáticas
            return static(dniback)
        else:
            return ''

    @property
    def name(self):
        if self.first_name:
            return self.first_name
        elif self.display_name:
            return self.display_name
        return 'You'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def guess_display_name(self):
        """Set a display name, if one isn't already set."""
        if self.display_name:
            return

        if self.first_name and self.last_name:
            dn = "%s %s" % (self.first_name, self.last_name[0])  # like "Andrew E"
        elif self.first_name:
            dn = self.first_name
        else:
            dn = 'You'
        self.display_name = dn.strip()

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def __str__(self):
        return self.email

    def natural_key(self):
        return (self.email,)

# Negocio (objeto)
class Negocio(CommonInfo, BaseActivatableModel):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    administrador = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='negocios')
    direccion_fiscal = models.CharField(_('Direccion'), max_length=100)
    localidad_fiscal = models.CharField(_('Localidad'), max_length=100)
    provincia_fiscal = models.CharField(_('Provincia'), max_length=100)
    codigo_postal_fiscal = models.CharField(_('Código Postal'), max_length=100)
    is_active = models.BooleanField(_('Activo'), default=True)
    aforo = models.PositiveSmallIntegerField(_('Aforo') )
    fechaRegistro = models.DateTimeField('Fecha Registro', auto_now_add=True, db_index=True)

    def _get_uso_actual(self):
        "Busca la lista de clientes actual."
        return 0
    uso_actual = property(_get_uso_actual)

    REQUIRED_FIELDS = ['nombre', 'administrador']
    class Meta:
        verbose_name = ('Negocio')
        verbose_name_plural = ('Negocios')

class AccesosManager(models.Manager):
    def create_acceso(self, idNegocio, idUsuario, fechaEntrada):
        acceso = self.create(user=User.objects.get(pk=idUsuario), negocio=Negocio.objects.get(pk=idNegocio), fechaEntrada=fechaEntrada)
        return acceso

# Lista de accesos
class Accesos(CommonInfo, models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='accesosusuario')
    negocio = models.ForeignKey(Negocio, null=False, on_delete=models.CASCADE, related_name='accesosnegocio')
    fechaEntrada = models.DateTimeField(_('fecha entrada'))
    fechaSalida = models.DateTimeField(_('fecha salida'), default=timezone.now)

    objects = AccesosManager()

    @classmethod
    def create(cls, idNegocio, idUsuario, fechaEntrada):
        acceso = cls(negocio=idNegocio, user=idUsuario, fechaEntrada=fechaEntrada)
        # do something with the book
        return acceso

class AforoManager(models.Manager):
    def create_entrada(self, idNegocio, idUsuario):
        entrada = self.create(user=User.objects.get(pk=idUsuario), negocio=Negocio.objects.get(pk=idNegocio))
        return entrada

# Lista de aforo (usuarios en el local)
class Aforo(CommonInfo, models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='aforousuario')
    negocio = models.ForeignKey(Negocio, null=False, on_delete=models.CASCADE, related_name='aforonegocio')
    fechaEntrada = models.DateTimeField(_('fecha entrada'), auto_now_add=True, db_index=True)

    objects = AforoManager()

    @classmethod
    def create(cls, idNegocio, idUsuario):
        entrada = cls(user=idUsuario, negocio=idNegocio)
        # do something with the book
        return entrada

@receiver(user_signed_up)
def set_initial_user_names(request, user, sociallogin=None, **kwargs):
    """
    When a social account is created successfully and this signal is received,
    django-allauth passes in the sociallogin param, giving access to metadata on the remote account, e.g.:
 
    sociallogin.account.provider  # e.g. 'twitter' 
    sociallogin.account.get_avatar_url()
    sociallogin.account.get_profile_url()
    sociallogin.account.extra_data['screen_name']
 
    See the socialaccount_socialaccount table for more in the 'extra_data' field.

    From http://birdhouse.org/blog/2013/12/03/django-allauth-retrieve-firstlast-names-from-fb-twitter-google/comment-page-1/
    """

    preferred_avatar_size_pixels = 256

    picture_url = "http://www.gravatar.com/avatar/{0}?s={1}".format(
        hashlib.md5(user.email.encode('UTF-8')).hexdigest(),
        preferred_avatar_size_pixels
    )

    if sociallogin:
        # Extract first / last names from social nets and store on User record
        if sociallogin.account.provider == 'twitter':
            name = sociallogin.account.extra_data['name']
            user.first_name = name.split()[0]
            user.last_name = name.split()[1]

        if sociallogin.account.provider == 'facebook':
            user.first_name = sociallogin.account.extra_data['first_name']
            user.last_name = sociallogin.account.extra_data['last_name']
            # verified = sociallogin.account.extra_data['verified']
            picture_url = "http://graph.facebook.com/{0}/picture?width={1}&height={1}".format(
                sociallogin.account.uid, preferred_avatar_size_pixels)

        if sociallogin.account.provider == 'google':
            user.first_name = sociallogin.account.extra_data['given_name']
            user.last_name = sociallogin.account.extra_data['family_name']
            # verified = sociallogin.account.extra_data['verified_email']
            picture_url = sociallogin.account.extra_data['picture']

    user.guess_display_name()
    user.save()
