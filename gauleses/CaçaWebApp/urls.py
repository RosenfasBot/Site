"""CaçaWebApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
import artefatos.views as ArtefatosViews
import users.views as usersViews
from django.conf.urls import include, static
import logs.views as logsViews
import caminhos.views as caminhosViews
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.conf import settings
import gerencial.views as gerencialViews

urlpatterns = [
    # Geral
    path('painel_admin/', admin.site.urls),
    path('conta/login/', usersViews.MyLoginView.as_view(), name='login'),
    path('conta/', include('django.contrib.auth.urls')),

    # Comum
    path("", TemplateView.as_view(template_name='comum/pagInicial.html'), name="paginaInicial"),
    path("vemcorrercomnois/", TemplateView.as_view(template_name='comum/vemcorrercomnois.html'), name="vemcorrercomnois"),

    # Dash
    path("dashboard/", login_required(caminhosViews.caca_dashboard), name="dashboard"),
    
    path('sessoes/', login_required(usersViews.sessions), name="sessions"),
    path('sessoes/deslogar/<str:pk>', login_required(usersViews.SessionDeleteView.as_view()), name='delete_session'),
    path('logs/', login_required(logsViews.view_logs), name='logs'),

    # Apps
    path('pistas/', include('pistas.urls')),
    path('', include('fila.urls')),
    
    path('gerencial/', include('gerencial.urls')),
    path('caminhos/', include('caminhos.urls')),
    path('artefatos/', include('artefatos.urls')),
    path('desejos/', include('desejos.urls')),
    path('usuarios/', include('users.urls')),

] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)