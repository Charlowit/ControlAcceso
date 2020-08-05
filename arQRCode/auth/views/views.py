from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import get_template
from django.views.generic.edit import FormMixin, UpdateView
from django.shortcuts import redirect
from django.conf import settings
from arQRCode.auth.forms.forms import UserEditForm


def index(request):
    # Haremos una cosa u otra en función de si hay un usuario autentificado o no
    if request.user.is_authenticated:
        return redirect('user_home')
    else:
        t = get_template('visitor/index.html')
        c = {}  #{'foo': 'bar'}
        return HttpResponse(t.render(c, request), content_type='text/html')

@login_required
def member_index(request):
    # Haremos una cosa u otra en función del tipo de usuario

    if request.user.is_authenticated:
        if request.user.is_business:
            return redirect('empresas:negocio_change_list')
        else:
            return redirect('usuarios:usuario_change_list')
    else:
        t = get_template('visitor/index.html')
    c = {}  #{'foo': 'bar'}
    return HttpResponse(t.render(c, request), content_type='text/html')

@login_required
def member_action(request):
    t = get_template('member/member-action.html')
    c = {}  #{'foo': 'bar'}
    return HttpResponse(t.render(c, request), content_type='text/html')

class MyModelInstanceMixin(FormMixin):
    def get_model_instance(self):
        return None

    def get_form_kwargs(self):
        kwargs = super(MyModelInstanceMixin, self).get_form_kwargs()
        instance = self.get_model_instance()
        if instance:
            kwargs.update({'instance': instance})
        return instance


class UserEditView(UpdateView):
    """Allow view and update of basic user data.

    In practice this view edits a model, and that model is
    the User object itself, specifically the names that
    a user has.

    The key to updating an existing model, as compared to creating
    a model (i.e. adding a new row to a database) by using the
    Django generic view ``UpdateView``, specifically the
    ``get_object`` method.
    """
    form_class = UserEditForm
    template_name = "auth/profile.html"
    view_name = 'account_profile'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, 'User profile updated')
        return super(UserEditView, self).form_valid(form)

    def get_success_url(self):
        #return reverse('empresas:negocio_change', kwargs={'pk': self.object.pk})
        return reverse('landing_index')


account_profile = login_required(UserEditView.as_view())



#### PRUEBA DE VUE ####
import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from io import StringIO
import base64
from PIL import Image
from pathlib import Path
import os
def registraEntrada(request):
    context = {}
    return render(request, 'list.html', context)

# ajax_posting function
def ajax_posting(request):
    if request.is_ajax():
        dniFrontImgBase64 = request.POST.get('dniFrontImgBase64', None) # getting data from input first_name id
        dniBackImgBase64 = request.POST.get('dniBackImgBase64', None)  # getting data from input last_name id
        identificacionTxt = request.POST.get('identificacionTxt', None)  # getting data from input last_name id

        print(dniFrontImgBase64)
        #print(dniBackImgBase64)
        #print(identificacionTxt)

        f = open( 'some_file.txt', 'w+')
        f.write(dniFrontImgBase64)
        f.close()

        import base64
        data = dniFrontImgBase64.replace(' ', '+')
        imgdata = base64.b64decode(data)
        filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
        with open(filename, 'wb') as f:
            f.write(imgdata)

        # Grabamos la imagen delantera
        if dniFrontImgBase64:
            destino = os.path.join(settings.PROFILEMEDIA_ROOT, identificacionTxt)
            Path(destino).mkdir(parents=True, exist_ok=True)
            imagenDNIDelantera = os.path.join(destino, '{0}-front.png'.format(identificacionTxt))
            pic = StringIO()
            image_string = StringIO(base64.b64decode(dniFrontImgBase64))
            image = Image.open(imagenDNIDelantera)
            image.save(pic, image.format, quality = 100)
            pic.seek(0)
        # Grabamos la imagen trasera
        if dniBackImgBase64:
            destino = os.path.join(settings.PROFILEMEDIA_ROOT, identificacionTxt)
            Path(destino).mkdir(parents=True, exist_ok=True)
            imagenDNITrasera = os.path.join(destino, '{0}-back.png'.format(identificacionTxt))
            pic = StringIO()
            image_string = StringIO(base64.b64decode(dniFrontImgBase64))
            image = Image.open(imagenDNITrasera)
            image.save(pic, image.format, quality = 100)
            pic.seek(0)

        # Grabamos el registro de la entrada/salida

        return JsonResponse({'success': True})
