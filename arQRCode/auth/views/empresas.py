from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, FormView, TemplateView)
from django.utils import timezone

from django.http import HttpResponse
from django.template.loader import get_template

from ..decorators import empresa_required
# from ..forms import BaseAnswerInlineFormSet, QuestionForm, TeacherSignUpForm
from ..models import Negocio, Aforo, User, Accesos
from ..forms.empresas import RegistroForm
#
@method_decorator([login_required, empresa_required], name='dispatch')
class NegociosListView(ListView):
    model = Negocio
    ordering = ('nombre', )
    context_object_name = 'negocios'
    template_name = 'auth/empresas/negocio_change_list.html'
#    paginate_by = 10
    def get_queryset(self):
        try:
            queryset = self.request.user.negocios
        except Exception as e:
            print(e)

        return queryset

@method_decorator([login_required, empresa_required], name='dispatch')
class NegocioCreateView(CreateView):
    model = Negocio
    readonly_fields=('fechaRegistro', )
    fields = ('nombre', 'direccion_fiscal', 'localidad_fiscal', 'provincia_fiscal', 'codigo_postal_fiscal', 'is_active', 'aforo', )
    template_name = 'auth/empresas/negocio_add_form.html'

    def form_valid(self, form):
        negocio = form.save(commit=False)
        negocio.administrador = self.request.user
        negocio.fechaRegistro = timezone.now
        negocio.save()
        messages.success(self.request, 'El negocio se ha creado correctamente.')
        return redirect('empresas:negocio_change_list')

@method_decorator([login_required, empresa_required], name='dispatch')
class NegocioUpdateView(UpdateView):
    model = Negocio
    readonly_fields=('fechaRegistro', )
    fields = ('nombre', 'direccion_fiscal', 'localidad_fiscal', 'provincia_fiscal', 'codigo_postal_fiscal', 'is_active', 'aforo', )
    context_object_name = 'negocio'
    template_name = 'auth/empresas/negocio_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['accesosnegocio'] = self.get_object().accesosnegocio
        kwargs['aforonegocio'] = self.get_object().aforonegocio
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.negocios.all()

    def get_success_url(self):
        #return reverse('empresas:negocio_change', kwargs={'pk': self.object.pk})
        return reverse('empresas:negocio_change_list')

@method_decorator([login_required, empresa_required], name='dispatch')
class NegocioAccesosView(UpdateView):
    model = Negocio
    readonly_fields=('fechaRegistro', )
    fields = ('nombre', 'direccion_fiscal', 'localidad_fiscal', 'provincia_fiscal', 'codigo_postal_fiscal', 'is_active', 'aforo', )
    context_object_name = 'negocio'
    template_name = 'auth/empresas/negocio_accesos_list.html'

    def get_context_data(self, **kwargs):
        kwargs['accesosnegocio'] = self.get_object().accesosnegocio
        kwargs['aforonegocio'] = self.get_object().aforonegocio
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.negocios.all()

    def get_success_url(self):
        return reverse('empresas:negocio_change', kwargs={'pk': self.object.pk})

@method_decorator([login_required, empresa_required], name='dispatch')
class NegocioDeleteView(DeleteView):
    model = Negocio
    context_object_name = 'negocio'
    template_name = 'auth/empresas/negocio_delete_confirm.html'
    success_url = reverse_lazy('empresas:negocio_change_list')

    def delete(self, request, *args, **kwargs):
        negocio = self.get_object()
########
# revisar por que no se borran los registros
########
        messages.success(request, 'El negocio %s se ha borrado correctamente!' % negocio.nombre)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.negocios.all()

# @method_decorator([login_required, empresa_required], name='dispatch')
# class RegistroView(CreateView):
#     model = User
#     fields = ('email', 'first_name', 'last_name', 'phone', )
#     template_name = 'auth/empresas/negocio_registro.html'
#     context_object_name = 'user'
#     success_url = reverse_lazy('empresas:negocio_registro')
#     form_class = RegistroForm
#     # def form_valid(self, form):
#     #     # Comprobamos si existe el usuario
#
#     def get_queryset(self):
#         '''
#         This method is an implicit object-level permission management
#         This view will only match the ids of existing quizzes that belongs
#         to the logged in user.
#         '''
#         return self.request.user
#
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Overridden so we can make sure the `Ipsum` instance exists
#         before going any further.
#         """
#         self.negocio = get_object_or_404(Negocio, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)
#
#     # Pasamos el id del negocio con el que vamos a trabajar
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a contexts
#         context = super(RegistroView, self).get_context_data(**kwargs)
#         # Pasamoe el ID del negocio a la vista
#         context['negocio'] = self.negocio
#         return context
#
#     def form_valid(self, form, **kwargs):
#         # Leemos la referencia al negocio
#         context = self.get_context_data(**kwargs)
#         negocio = context['negocio']
#         # Comprobamos si existe un usuario con el mail indicado y si no lo creamos
#         email = form.cleaned_data['email']
#         first_name = form.cleaned_data['first_name']
#         last_name = form.cleaned_data['last_name']
#         phone = form.cleaned_data['phone']
#         password = User.objects.make_random_password()
#         # Leemos el usuario o lo creamos en caso de que no exista
#         user = None
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, phone=phone)
#         # Creamos el registro de la entrada para el usuario indicado
#         try:
#             # Datos del registro de entrada
#             aforo = Aforo.objects.get(user=user.id, negocio=negocio.id)
#             # Generamos el registro de salida
#             acceso = Accesos.objects.create_acceso(aforo.negocio.id, aforo.user.id, aforo.fechaEntrada)
#             # y borramos el registro del aforo
#             aforo.delete()
#         except Aforo.DoesNotExist:
#             # Si no hay entrada => La creamos
#             entrada = Aforo.objects.create_entrada(negocio.id, user.id)
#
#         # Indicamos que el registro se ha creado correctamente
#         messages.add_message(self.request, messages.INFO, 'Registro creado correctamente.')
#         return self.render_to_response(self.get_context_data(form=form))
#         # model = form.save(commit=False)
#         # model.submitted_by = self.request.user
#         # model.save()
#         # return HttpResponseRedirect(self.get_success_url())
#
#     def get_success_url(self):
#         return reverse('demos-ui-createview')
#
#     def post(self, request, pk):
#         if self.form_valid(self.get_form(self.form_class)):
#             messages.add_message(self.request, messages.INFO, 'Registro creado correctamente.')
#         return redirect(request.META['HTTP_REFERER'])
# #********
# #Validar el form y grabar la información
# #********
#
#         #return redirect('empresas:negocio_registro', pk)

# #@method_decorator([login_required, empresa_required], name='dispatch')
# def RegistroView(request, pk):
#      submitted = False
#      if request.method == 'POST':
#          form = RegistroForm(request.POST)
#          if form.is_valid():
#              # assert False
#              return redirect(request.META['HTTP_REFERER'])
#      else:
#          form = RegistroForm()
#          if 'submitted' in request.GET:
#              submitted = True
#
#      return render(request,
#          'auth/empresas/negocio_registro.html',
#          {'form': form, 'submitted': submitted}
#          )

# @method_decorator([login_required, empresa_required], name='dispatch')
# class RegistroView(FormView):
#     template_name = 'auth/empresas/negocio_registro.html'
#
#     def dispatch(self, request, *args, **kwargs):
#         """
#         Overridden so we can make sure the `Ipsum` instance exists
#         before going any further.
#         """
#         self.negocio = get_object_or_404(Negocio, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)
#
#     # Pasamos el id del negocio con el que vamos a trabajar
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a contexts
#         context = super(RegistroView, self).get_context_data(**kwargs)
#         # Pasamoe el ID del negocio a la vista
#         context['negocio'] = self.negocio
#         # Registramos el formulario
#         form = RegistroForm()  # instance= None
#         context['form'] = form
#         return context
#
#     # def form_valid(self, form, **kwargs):
#     #     # Leemos la referencia al negocio
#     #     context = self.get_context_data(**kwargs)
#     #     negocio = context['negocio']
#     #     # Comprobamos si existe un usuario con el mail indicado y si no lo creamos
#     #     email = form.cleaned_data['email']
#     #     first_name = form.cleaned_data['first_name']
#     #     last_name = form.cleaned_data['last_name']
#     #     phone = form.cleaned_data['phone']
#     #     password = User.objects.make_random_password()
#     #     # Leemos el usuario o lo creamos en caso de que no exista
#     #     user = None
#     #     try:
#     #         user = User.objects.get(email=email)
#     #     except User.DoesNotExist:
#     #         user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, phone=phone)
#     #     # Creamos el registro de la entrada para el usuario indicado
#     #     try:
#     #         # Datos del registro de entrada
#     #         aforo = Aforo.objects.get(user=user.id, negocio=negocio.id)
#     #         # Generamos el registro de salida
#     #         acceso = Accesos.objects.create_acceso(aforo.negocio.id, aforo.user.id, aforo.fechaEntrada)
#     #         # y borramos el registro del aforo
#     #         aforo.delete()
#     #     except Aforo.DoesNotExist:
#     #         # Si no hay entrada => La creamos
#     #         entrada = Aforo.objects.create_entrada(negocio.id, user.id)
#     #
#     #     # Indicamos que el registro se ha creado correctamente
#     #     messages.add_message(self.request, messages.INFO, 'Registro creado correctamente.')
#     #     return self.render_to_response(self.get_context_data(form=form))
#     #     # model = form.save(commit=False)
#     #     # model.submitted_by = self.request.user
#     #     # model.save()
#     #     # return HttpResponseRedirect(self.get_success_url())
#
#     def post(self, request, pk):
#         form = RegistroForm(self.request.POST or None)
#
#         if form.is_valid():
#             messages.add_message(self.request, messages.INFO, 'Registro creado correctamente.')
#         else:
#             messages.add_message(self.request, messages.ERROR, 'Error en el formulario.')
#         return redirect(request.META['HTTP_REFERER'])
# #********
# #Validar el form y grabar la información
# #********
#
#         #return redirect('empresas:negocio_registro', pk)

@method_decorator([login_required, empresa_required], name='dispatch')
class RegistroView(FormView):
    form_class = RegistroForm
    template_name = 'auth/empresas/negocio_registro.html'
    success_url = reverse_lazy('empresas:negocio_registro')

    def form_valid(self, form):
        return super(RegistroView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the `Ipsum` instance exists
        before going any further.
        """
        self.negocio = get_object_or_404(Negocio, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        context['form'] = form
        return self.render_to_response(context)

    # Pasamos el id del negocio con el que vamos a trabajar
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a contexts
        context = super(RegistroView, self).get_context_data(**kwargs)
        # Pasamoe el ID del negocio a la vista
        context['negocio'] = self.negocio
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            # Procesamos la información del formulario.
            self.procesaFormulario(request, form, *args, **kwargs)
#            return self.render_to_response(self.get_context_data(form=form))
            return redirect('empresas:negocio_registro', *args, **kwargs)
        else:
            return self.form_invalid(form, **kwargs)

    def procesaFormulario(self, request, form, *args, **kwargs):
        # Leemos la referencia al negocio
        print(form.cleaned_data)
        context = self.get_context_data(form=form)
        negocio = context['negocio']
        # Comprobamos si existe un usuario con el mail indicado y si no lo creamos
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        phone = form.cleaned_data['phone']
        dni = form.cleaned_data['dni']
        password = User.objects.make_random_password()
        # Leemos el usuario o lo creamos en caso de que no exista
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, phone=phone, dni=dni)
        # Creamos el registro de la entrada para el usuario indicado
        try:
            # Datos del registro de entrada
            aforo = Aforo.objects.get(user=user.id, negocio=negocio.id)
            # Generamos el registro de salida
            acceso = Accesos.objects.create_acceso(aforo.negocio.id, aforo.user.id, aforo.fechaEntrada)
            # y borramos el registro del aforo
            aforo.delete()
        except Aforo.DoesNotExist:
            # Si no hay entrada => La creamos
            entrada = Aforo.objects.create_entrada(negocio.id, user.id)

        # Indicamos que el registro se ha creado correctamente
        messages.add_message(self.request, messages.INFO, 'Registro creado correctamente.')
#       return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)