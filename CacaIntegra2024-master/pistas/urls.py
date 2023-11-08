from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'pistas'
urlpatterns = [
    path('criar/', login_required(views.PistaCreateView.as_view()), name='create_pista'),
    path('ver/<str:pk>/', login_required(views.PistaReadView.as_view()), name='detail_pista'),
    path('editar/<str:pk>/', login_required(views.PistaEditView.as_view()), name='update_pista'),
    path('deletar/<str:pk>', login_required(views.PistaDeleteView.as_view()), name='delete_pista'),

    path('detalhes/<str:pk>/', login_required(views.view_pista_CA), name='detail_pista_CA'),

    path('carregarPistas/', login_required(views.carregar_pistas), name='carregar_pistas'),
    path('resetarPistas/', login_required(views.resetar_pistas), name='resetar_pistas'),
    path('deletarPistas/', login_required(views.deletar_pistas), name='deletar_pistas'),

    path('deletarSenha/', login_required(views.deletar_senhas), name='deletar_senhas'),

    path('senhas', login_required(views.view_senhas), name='allSenhas'),
    path('queimarSenha', login_required(views.queima_senhas), name='queimaSenha'),
    path('exportarSenhas', login_required(views.todas_senhas), name='todas_senhas'),

    path('carregarSenhas/', login_required(views.BatchSenhaView.as_view()), name='carregar_senhas'),

    path('plantar/<str:pk>/', login_required(views.PistaPlantarView.as_view()), name='plantar_pista'),
    path('', login_required(views.view_pistas), name='allPistas'),
]
