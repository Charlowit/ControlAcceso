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
                                  UpdateView, FormView)
from django.utils import timezone

from ..decorators import empresa_required
# from ..forms import BaseAnswerInlineFormSet, QuestionForm, TeacherSignUpForm
from ..models import Negocio, Aforo #Answer, Question, Quiz, User
#
@method_decorator([login_required, empresa_required], name='dispatch')
class NegociosListView(ListView):
    model = Negocio
    ordering = ('nombre', )
    context_object_name = 'negocios'
    template_name = 'auth/empresas/negocio_change_list.html'
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
        return redirect('empresas:negocio_change', negocio.pk)

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

@method_decorator([login_required, empresa_required], name='dispatch')
class RegistroView(UpdateView):
    model = Negocio
    readonly_fields=('fechaRegistro', )
    fields = ('nombre', 'direccion_fiscal', 'localidad_fiscal', 'provincia_fiscal', 'codigo_postal_fiscal', 'is_active', 'aforo', )
    context_object_name = 'negocio'
#    template_name = 'auth/empresas/negocio_registro.html'
    template_name = 'auth/empresas/negocio_registro.html'
    success_url = reverse_lazy('empresas:negocio_change_list')

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
        return reverse('empresas:negocio_registro', kwargs={'pk': self.object.pk})
