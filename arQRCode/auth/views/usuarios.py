import os
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
from django.templatetags.static import static
from django.conf import settings

from ..decorators import usuario_required

from ..models import User, Accesos

@method_decorator([login_required, usuario_required], name='dispatch')
class UsuariosListView(ListView):
    model = Accesos
    ordering = ('-fechaEntrada', )
    context_object_name = 'accesos'
    template_name = 'auth/usuarios/usuario_change_list.html'
    # paginate_by = 10

    # Calculamos las URL de las imágenes del usuario.
    def get_context_data(self, **kwargs):
        user = self.request.user
        # Call the base implementation first to get a contexts
        context = super(UsuariosListView, self).get_context_data(**kwargs)
        context['urldnifront'] = user.get_frontDNI_url()
        context['urldniback'] = user.get_backDNI_url()
        return context

    def get_queryset(self):
        try:
            queryset = self.request.user.accesosusuario
        except Exception as e:
            print(e)
        return queryset
