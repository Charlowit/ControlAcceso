"""arQRCode URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.generic import TemplateView
from .auth.views.views import account_profile

urlpatterns = [
    # Landing page area
#    url(r'^$', TemplateView.as_view(template_name='visitor/landing-index.html'), name='landing_index'),
    path('', include('arQRCode.auth.urls')),
    # Account management is done by allauth
    url(r'^accounts/', include('allauth.urls')),
    # Usual Django admin
    url(r'^admin/', admin.site.urls),

    # url(r'^$', TemplateView.as_view(template_name='visitor/index.html'), name='landing_index'),
    # url(r'^manual$', TemplateView.as_view(template_name='visitor/manual.html'), name='landing_manual'),
    # url(r'^about$', TemplateView.as_view(template_name='visitor/landing-about.html'), name='landing_about'),
    # url(r'^terms/$', TemplateView.as_view(template_name='visitor/terms.html'), name='website_terms'),
    # url(r'^contact$', TemplateView.as_view(template_name='visitor/contact.html'), name='website_contact'),
    # # Account profile and member info done locally
    # url(r'^accounts/profile/$', account_profile, name='account_profile'),
    # url(r'^member/$', member_index, name='user_home'),
    # url(r'^member/action$', member_action, name='user_action'),
    #
    #
    # ##### PRUEBA VUE #####
    # url(r'^registraEntrada/', registraEntrada, name='registraEntrada'),
    # path('ajax-posting/', ajax_posting, name='ajax_posting'),# ajax-posting / name = that we will use in ajax url
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

