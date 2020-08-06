from django.urls import include, path
from django.conf.urls import url
from django.views.generic import TemplateView
from .views import views, usuarios, empresas
from .views.views import account_profile, member_index, member_action, registraEntrada, ajax_posting, ajax_check, ajax_salida

urlpatterns = [
#    path('', views.home, name='home'),
    url(r'^$', views.index, name='landing_index'),
    url(r'^manual$', TemplateView.as_view(template_name='visitor/manual.html'), name='landing_manual'),
    url(r'^about$', TemplateView.as_view(template_name='visitor/landing-about.html'), name='landing_about'),
    url(r'^terms/$', TemplateView.as_view(template_name='visitor/terms.html'), name='website_terms'),
    url(r'^contact$', TemplateView.as_view(template_name='visitor/contact.html'), name='website_contact'),
    url(r'^legal$', TemplateView.as_view(template_name='visitor/landing-legal.html'), name='landing_legal'),
    url(r'^privacidad/$', TemplateView.as_view(template_name='visitor/privacidad.html'), name='privacidad'),
    url(r'^cookies$', TemplateView.as_view(template_name='visitor/cookies.html'), name='cookies'),

    url(r'^accounts/profile/$', account_profile, name='account_profile'),
    url(r'^member/$', member_index, name='user_home'),
    path('empresas/', include(([
        path('', empresas.NegociosListView.as_view(), name='negocio_change_list'),
        path('negocio/add/', empresas.NegocioCreateView.as_view(), name='negocio_add'),
        path('negocio/<int:pk>/', empresas.NegocioUpdateView.as_view(), name='negocio_change'),
        path('negocio/<int:pk>/accesos/', empresas.NegocioAccesosView.as_view(), name='negocio_accesos'),
        path('negocio/<int:pk>/delete/', empresas.NegocioDeleteView.as_view(), name='negocio_delete'),
        path('negocio/<int:pk>/registro/', empresas.RegistroView.as_view(), name='negocio_registro'),
#        path('negocio/<int:pk>/registro/', empresas.RegistroView, name='negocio_registro'),
        ##### PRUEBA VUE #####
        url(r'^registraEntrada/', registraEntrada, name='registraEntrada'),
        path('ajax-posting/', ajax_posting, name='ajax_posting'),# ajax-posting / name = that we will use in ajax url
        path('ajax-check/', ajax_check, name='ajax_check'),
        path('ajax-salida/', ajax_salida, name='ajax_salida'),

    ], 'arQRCode'), namespace='empresas')),
    path('usuarios/', include(([
#        path('', TemplateView.as_view(template_name='auth/usuarios/usuario_change_list.html'), name='usuario_change_list'),
        path('', usuarios.UsuariosListView.as_view(), name='usuario_change_list'),
    ], 'arQRCode'), namespace='usuarios')),

    # path('students/', include(([
    #     path('', students.QuizListView.as_view(), name='quiz_list'),
    #     path('interests/', students.StudentInterestsView.as_view(), name='student_interests'),
    #     path('taken/', students.TakenQuizListView.as_view(), name='taken_quiz_list'),
    #     path('quiz/<int:pk>/', students.take_quiz, name='take_quiz'),
    # ], 'classroom'), namespace='students')),
    #
    # path('teachers/', include(([
    #     path('', teachers.QuizListView.as_view(), name='quiz_change_list'),
    #     path('quiz/add/', teachers.QuizCreateView.as_view(), name='quiz_add'),
    #     path('quiz/<int:pk>/', teachers.QuizUpdateView.as_view(), name='quiz_change'),
    #     path('quiz/<int:pk>/delete/', teachers.QuizDeleteView.as_view(), name='quiz_delete'),
    #     path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
    #     path('quiz/<int:pk>/question/add/', teachers.question_add, name='question_add'),
    #     path('quiz/<int:quiz_pk>/question/<int:question_pk>/', teachers.question_change, name='question_change'),
    #     path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', teachers.QuestionDeleteView.as_view(), name='question_delete'),
    # ], 'classroom'), namespace='teachers')),
]
