from django import forms
from django.forms import ModelForm
from ..models import User

class RegistroForm(forms.Form):
    # class Meta:
    #     model = User
    #     fields = ('email', 'first_name', 'last_name', 'phone', )

    email = forms.EmailField(label='email:',max_length=50)
    first_name = forms.CharField(label='Nombre:',max_length=150,required=False)
    last_name = forms.CharField(label='Apellidos:',max_length=150,required=False)
    phone = forms.CharField(label='Teléfono',max_length=15,required=True)
    dni = forms.CharField(label='DNI', max_length=10, required=True)
#
# class RegistroForm(CrispyForm):
#     def __init__(self, *args, **kwargs):
#         super(SomeItemAddForm, self).__init__(*args, form_action='add-someitem', **kwargs)
#
#     class Meta:
#         model = SomeItem
#         fields = '__all__'
