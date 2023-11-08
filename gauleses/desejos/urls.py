from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'desejos'
urlpatterns = [
    path('criar/', login_required(views.DesejoCreateView.as_view()), name='create_desejo'),
    path('editar/<int:pk>/', login_required(views.DesejoEditView.as_view()), name='update_desejo'),
    path('deletar/<int:pk>', login_required(views.DesejoDeleteView.as_view()), name='delete_desejo'),
    path('allDesejos', login_required(views.view_desejos), name='allDesejos'),
    path('', views.desejos_page, name='desejos'),
]
