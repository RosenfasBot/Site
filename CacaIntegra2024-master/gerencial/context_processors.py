# as funçoes definidas no context_processor retornam variaveis que ficam disponiveis em todas as páginas
# obs: as funções ainda tem que ficar declaradas no settings.py

from .models import Gerencial
from django.conf import settings

def gerencial(request):
    return {'gerencial': Gerencial.load()}

def recaptcha(request):
    return {'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_SITE_KEY}