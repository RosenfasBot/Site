from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'caminhos'
urlpatterns = [
    path('criar/', login_required(views.CaminhoCreateView.as_view()), name='create_caminho'),
    path('ver/<int:pk>/', login_required(views.CaminhoReadView.as_view()), name='detail_caminho'),
    path('editar/<int:pk>/', login_required(views.CaminhoEditView.as_view()), name='update_caminho'),
    path('deletar/<int:pk>', login_required(views.CaminhoDeleteView.as_view()), name='delete_caminho'),

    path('criarCorte/', login_required(views.CorteCreateView.as_view()), name='create_corte'),
    path('deletarCorte/<int:pk>', login_required(views.CorteDeleteView.as_view()), name='delete_corte'),
    path('cortes', login_required(views.view_cortes), name='allCortes'),

    path('', login_required(views.view_caminhos), name='allCaminhos'),
]
