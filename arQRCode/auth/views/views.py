from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import get_template
from django.views.generic.edit import FormMixin, UpdateView
from django.shortcuts import redirect
from django.conf import settings
from arQRCode.auth.forms.forms import UserEditForm
import logging
logger = logging.getLogger(__name__)

from ..models import User, Aforo, Accesos
from django.db import transaction

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
import base64

def registraEntrada(request):
    context = {}
    return render(request, 'list.html', context)

# ajax_posting function
def saveBase64Image(img, ruta):
    # Preparamos la imagen
    data = img.replace('data:image/png;base64,', '')
    data = data.replace(' ', '+')
    # y la decodificamos
    imgdata = base64.b64decode(data)
    # La guardamos en el fichero indicado
    with open(ruta, 'wb') as f:
        f.write(imgdata)

@login_required
def ajax_posting(request):
    if request.is_ajax():
        # Leemos la petición del request
        conDNI = request.POST.get('conDNI', None)
        dniFrontImgBase64 = request.POST.get('dniFrontImgBase64', None) # getting data from input first_name id
        dniBackImgBase64 = request.POST.get('dniBackImgBase64', None)  # getting data from input last_name id
        identificacionTxt = request.POST.get('identificacionTxt', None)  # getting data from input last_name id
        negocioId = request.POST.get('negocioId', None)  # getting data from input negocio ID
        # Grabamos la imagen delantera si viene con DNI
        if conDNI == 'true':
            # Comprobamos que exista el directorio
            directorio = os.path.join(settings.PROFILEMEDIA_ROOT, identificacionTxt)
            try:
                os.mkdir(directorio)
            except OSError:
                logger.error("Creation of the directory %s failed" % directorio)
            else:
                logger.error("Successfully created the directory %s " % directorio)
            # Calculamos los nombres de las imagenes para el usuario
            rutafront = os.path.join(directorio, settings.DNIFRONT)
            rutaback = os.path.join(directorio, settings.DNIBACK)

            if dniFrontImgBase64:
                # Usamos la función
                saveBase64Image(dniFrontImgBase64, rutafront)
            # Grabamos la imagen trasera
            if dniBackImgBase64:
                # Usamos la función
                saveBase64Image(dniBackImgBase64, rutaback)

        # Grabamos el registro de la entrada/salida
        entrada = Aforo.objects.create_entrada(negocioId, identificacionTxt)

        # Llamamos a la función del modelo para hacer el apunte
        return JsonResponse({'success': True})

@login_required
def ajax_check(request):
    if request.is_ajax():
        # Leemos la petición del request
        identificacionTxt = request.POST.get('identificacionTxt', None)  # getting data from input user UUID
        negocioId = request.POST.get('negocioId', None)  # getting data from input negocio ID
        # Buscamos el usuario
        try:
            user = User.objects.get(pk = identificacionTxt)
            # Verificamos el estado del usuario
            try:
                aforo = Aforo.objects.get(user=identificacionTxt, negocio=negocioId)
                # Devolvemos el estado de acceso
                return JsonResponse({'success': aforo.fechaEntrada})
            except Exception:
                # Además del error, devolvemos las URL de las imágenes (si existen)
                # Obtenemos la referencia al usuario
                response = {'error': True}
                urldnifront = user.get_frontDNI_url()
                urldniback = user.get_backDNI_url()
                if urldnifront != '':
                    response['urldnifront'] = urldnifront
                if urldniback != '':
                    response['urldniback'] = urldniback
                return JsonResponse(response)
        except User.DoesNotExist:
            # Obtenemos la referencia al usuario
            response = {'error': True}
            response['userExists'] = False
            return JsonResponse(response)

@login_required
@transaction.atomic
def ajax_salida(request):
    if request.is_ajax():
        # Leemos la petición del request
        identificacionTxt = request.POST.get('identificacionTxt', None)  # getting data from input user UUID
        negocioId = request.POST.get('negocioId', None)  # getting data from input negocio ID
        # Directamente generamos la salida
        # Verificamos el estado del usuario
        try:
            # Datos del registro de entrada
            aforo = Aforo.objects.get(user=identificacionTxt, negocio=negocioId)
            # Generamos el registro de salida
            acceso = Accesos.objects.create_acceso(aforo.negocio.id, aforo.user.id, aforo.fechaEntrada)
            # y borramos el registro del aforo
            aforo.delete()
            # Devolvemos el estado de acceso
            return JsonResponse({'success': acceso.fechaSalida})
        except Exception:
            # Si hay excepción => no estaba dentro => no hacemos nada
            return JsonResponse({'error': True})


