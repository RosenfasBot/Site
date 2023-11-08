from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'users'
urlpatterns = [
    path('criar/', login_required(views.UserCreateView.as_view()), name='create_user'),
    path('ver/<int:pk>/', login_required(views.UserReadView.as_view()), name='detail_user'),
    path('editar/<int:pk>/', login_required(views.UserEditView.as_view()), name='update_user'),
    path('deletar/<int:pk>', login_required(views.UserDeleteView.as_view()), name='delete_user')
]