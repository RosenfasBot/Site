from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'fila'
urlpatterns = [
    path('fila/aleatoria', login_required(views.fila_aleatoria), name='fila_aletoria'),
    path('fila/ver', login_required(views.view_fila), name='allFila'),
    
    path('fila/alterar', login_required(views.alterar_fila), name='alterarFila'),
    
    path('validar', login_required(views.validar_pista), name='validar_pista'),
    path('plantar/', login_required(views.plantar_pista), name='plantar')
]
