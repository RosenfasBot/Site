from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'gerencial'
urlpatterns = [
    path('criarLock/', login_required(views.WebSiteLockCreateView.as_view()), name='create_lock'),
    path('editar/<int:pk>/', login_required(views.WebSiteLockEditView.as_view()), name='update_lock'),
    path('deletar/<int:pk>', login_required(views.WebSiteLockDeleteView.as_view()), name='delete_lock'),
    path('', login_required(views.ViewGerencial), name='gerencial'),
    path('editTimeout', login_required(views.editTimeout), name='editTimeout'),
    path('timeoutCreate/', login_required(views.CreateTimeoutView.as_view()), name='createTimeout'),
    path('editGerencial/<int:pk>', login_required(views.GerencialEditView.as_view()), name='update_gerencial'),
    path('startCaca', login_required(views.startCaca), name='startCaca')
]