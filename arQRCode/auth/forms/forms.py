import os
from django import forms
from arQRCode.auth.models import User
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class UserEditForm(forms.ModelForm):
    """Form for viewing and editing name fields in a User object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """

    def __init__(self, *args, **kwargs):
        # TODO: this doesn't seem to work. Need to get to the bottom of it.
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'display_name', 'phone', 'dni', 'acceptPush', 'date_joined', 'is_business')

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'display_name', 'is_staff', 'is_active', 'date_joined')

    def is_valid(self):
        return super().is_valid()

#class qrCodeSignupForm(SignupForm):
    # def __init__(self, *args, **kwargs):
    #     super(qrCodeSignupForm, self).__init__(*args, **kwargs)
    #     self.fields['first_name'] = forms.CharField(required=True)
    #     self.fields['last_name'] = forms.CharField(required=True)
    #     self.fields['phone'] = forms.CharField(required=True)
    #     self.fields['acceptPush'] = forms.BooleanField(required=False)
    #     self.fields['is_business'] = forms.BooleanField(required=True)
    #
    # def save(self, request):
    #     phone = self.cleaned_data.pop('phone')
    #     acceptPush = self.cleaned_data.pop('acceptPush')
    #     is_business = self.cleaned_data.pop('is_business')
    #     user = super(qrCodeSignupForm, self).save(request)
    #     return user

from allauth.account.forms import SignupForm
class qrCodeSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(qrCodeSignupForm, self).__init__(*args, **kwargs)
        self.fields['phone'] = forms.CharField(required=True)
        self.fields['dni'] = forms.CharField(required=True)
        self.fields['first_name'] = forms.CharField(required=False)
        self.fields['last_name'] = forms.CharField(required=False)
        self.fields['is_business'] = forms.BooleanField(required=False)
        self.fields['acceptPush'] = forms.BooleanField(required=False)

    def save(self, request):
        is_business = self.cleaned_data.pop('is_business')
        acceptPush = self.cleaned_data.pop('acceptPush')
        phone = self.cleaned_data.pop('phone')
        dni = self.cleaned_data.pop('dni')
        first_name = self.cleaned_data.pop('first_name')
        last_name = self.cleaned_data.pop('last_name')
        user = super(qrCodeSignupForm, self).save(request)
        # campos personalizados
        user.is_business = is_business
        user.acceptPush = acceptPush
        user.phone = phone
        user.dni = dni
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        # Por último creamos las carpetas
        directorio = os.path.join(settings.PROFILEMEDIA_ROOT, str(user.id))
        try:
            os.mkdir(directorio)
        except OSError:
            logger.error("Creation of the directory %s failed" % directorio)
        else:
            logger.error("Successfully created the directory %s " % directorio)
        return user

