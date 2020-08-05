from django import forms

from arQRCode.auth.models import User

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
        fields = ('email', 'first_name', 'last_name', 'display_name', 'phone', 'acceptPush', 'date_joined', 'is_business')

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
        self.fields['phone'] = forms.CharField(required=False)
        self.fields['is_business'] = forms.BooleanField(required=True)
        self.fields['acceptPush'] = forms.BooleanField(required=True)

    def save(self, request):
        is_business = self.cleaned_data.pop('is_business')
        acceptPush = self.cleaned_data.pop('acceptPush')
        phone = self.cleaned_data.pop('phone')
        user = super(qrCodeSignupForm, self).save(request)
        return user

