from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

app_name = 'artefatos'
urlpatterns = [
    path('criar/', login_required(views.ArtefatoCreateView.as_view()), name='create_artefato'),
    path('ver/<int:pk>/', login_required(views.ArtefatoReadView.as_view()), name='detail_artefato'),
    path('editar/<int:pk>/', login_required(views.ArtefatoEditView.as_view()), name='update_artefato'),
    path('deletar/<int:pk>', login_required(views.ArtefatoDeleteView.as_view()), name='delete_artefato'),

    path('', TemplateView.as_view(template_name='comum/artefatos.html'), name="artefatos"),
    path('seeAll', login_required(views.view_artefatos), name='allArtefatos'),
]
