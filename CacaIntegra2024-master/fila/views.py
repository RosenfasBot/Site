from django.shortcuts import render
from django.conf import settings
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test
from .models import Fila
import requests
import pandas as pd
from django.http import HttpResponse

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO

from django.shortcuts import render
from gerencial.models import Gerencial
from gerencial.utils import SendTelegramMessage
from pistas.models import Senha, Pista
from fila.models import Fila
import requests
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.conf import settings
from django.utils import timezone
import random


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_fila(request):
    fila = Fila.load()
    pistas = fila.all_pistas
    context = {'pistas': pistas}
    return render(request, './fila/viewFila.html', context)



@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def alterar_fila(request):
    new_fila = [int(x) for x in request.POST['fila'].split(',')]
    print(new_fila)
    fila = Fila.load()
    fila.fila = new_fila
    fila.save()
    return HttpResponse(status=204)


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def plantar_pista(request):
    fila = Fila.load()
    pap = []
    if len(fila.fila)>0:
        pap = fila.pistas_a_plantar[:30]
    context = {'pistas': [(p, fila.index_pista(p)) for p in pap]}
    return render(request, './fila/plantarPista.html', context)


# carrega a ordem das pistas na fila a partir da planilha de pistas
@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def fila_aleatoria(request):
    numeros = [x.numero for x in Pista.objects.all()]
    fila = Fila.load()
    random.shuffle(numeros)
    fila.fila = numeros
    fila.save()
    return HttpResponse(status=200)


def avanca_nivel(request, request_body, userCA, pista):
    pista.status = 'recolhida'
    pista.last_modified_by = userCA.user.username

    # caso seja pista inicial compartilhada, atribuir o caminho ao CA que pegou
    if not pista.caminho.CA_ativo:
        caminho = pista.caminho
        caminho.CA_ativo = userCA
        caminho.save()
    pista.save()

    # caso seja a última pista do caminho
    if pista.caminho.progresso == pista.caminho.tamanho:
        SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {userCA.user.username} finalizou um de seus caminhos')
        return render(request, './fila/validarPistaResposta.html', {'senha': request_body['senha'], 'resposta': 'Caminho Finalizado!', 'context': 'Parabéns, vocês encerraram esse caminho!'})

    # caso não seja a última pista do caminho
    else:
        fila = Fila.load()
        proxima_pista = fila.get_proxima_pista(pista.caminho)
        proxima_pista.hora_inicio = timezone.now()
        proxima_pista.caminho = pista.caminho
        proxima_pista.save()

        return render(request, './fila/validarPistaResposta.html', {'senha': request_body['senha'], 'resposta': 'Pista Confirmada!', 'context': 'Parabéns, essa pista pertence ao CA! Volte ao Dashboard para visualizá-la'})


@user_passes_test(CA_check, login_url='login', redirect_field_name=None)
def validar_pista(request):
    if not (request.user.is_CA and request.user.is_authenticated and request.user.userca.is_radio):
        raise Http404()

    # GET: carregamento normal da página
    if request.method == 'GET':
        context = {'timeout': False}
        userCA = request.user.userca
        if userCA.timeout_until > timezone.now():
            context = {'timeout': True, 'until': userCA.timeout_until}
        return render(request, './fila/validarPista.html', context)

    # POST: usuário enviou uma tentativa de senha
    elif request.method == 'POST':
        request_body = request.POST

        # caso o POST venha vazio
        if not request_body:
            return None

        recaptcha_response = request_body['g-recaptcha-response']
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        # caso o captcha não tenha sido preenchido
        if not result['success']:
            return render(request, './fila/validarPista.html', {'erro': 'Preenche o captcha, seu bobão'})

        userCA = request.user.userca
        # caso o CA esteja em timeoout de pistas
        if userCA.timeout_until > timezone.now():
            context = {'timeout': True, 'until': userCA.timeout_until}
            return render(request, './fila/validarPista.html', context)

        senha_testada = request_body['senha']
        senha = Senha.objects.filter(valor=senha_testada).first()
        pista = Pista.objects.filter(senha=senha).first()
        # caso senha existe no caça - se não existe Typo ou BruteForce
        if senha:
            # queimar senha para não ser replantada
            senha.queimada = True
            senha.save()

            # caso senha de pista inválida, é Pré-Caça
            if not senha.valida:
                userCA.timeout_until = timezone.now() + timezone.timedelta(minutes=Gerencial.load().timeout_precaca)
                userCA.save()
                SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {userCA.user.username} foi pego fazendo pré-caça')
                return render(request, './fila/validarPistaResposta.html', {'senha': senha_testada, 'resposta': 'Você foi pego no pré-caça', 'context': 'Pode já avisar seus bixos que o caça começa daqui a '+str(Gerencial.load().timeout_precaca/60)+' horas'})

            # Senha já tenha sido validada pelo CA que está tentando ela
            if pista.caminho and pista.caminho.CA_ativo == userCA and pista.status == 'recolhida':
                return render(request, './fila/validarPistaResposta.html', {'senha': request_body['senha'], 'resposta': 'Pista já confirmada', 'context': 'Você já validou essa pista, volte ao dashboard para visualizá-la'})

            # Pista associada:
            if pista:
                # Se a pista está plantada
                if pista.status=='plantada':
                    # Pista certa
                    if pista.caminho and (pista.caminho.CA_ativo == userCA or not pista.caminho.CA_ativo) and pista.caminho.ativo and pista.caminho.pista_viva==pista:
                        return avanca_nivel(request, request_body, userCA, pista)
                    #Pista extraviada
                    else:
                        userCA.timeout_until = timezone.now() + timezone.timedelta(minutes=Gerencial.load().timeout_extravio)
                        userCA.save()
                        pista.status = 'extraviada'
                        pista.last_modified_by = userCA.user.username
                        pista.save()
                        # caso a pista não esteja atribuída ainda a um caminho: mandar para o final da fila
                        if not pista.caminho:
                            fila = Fila.load()
                            fila.manda_pro_fim(pista.numero)
                        SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Pista {pista.numero} extraviada por {userCA.user.username}')
                        return render(request, './fila/validarPistaResposta.html', {'senha': senha_testada, 'resposta': 'Pista Extraviada', 'context': 'Jogue a pista encontrada no lixo.<br>Você recebeu um timeout de '+str(Gerencial.load().timeout_extravio)+' minuto para tentar novamente'})

                # Pista já extraviada ou já confirmada por outro CA
                else:
                    userCA.timeout_until = timezone.now() + timezone.timedelta(minutes=Gerencial.load().timeout_merda)
                    userCA.save()
                    SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {userCA.user.username} fazendo merda, tentaram a senha {request_body["senha"]}')
                    return render(request, './fila/validarPistaResposta.html', {'senha': senha_testada,'resposta': 'Você tá errado!', 'context': 'Você tá fazendo merda, e estamos de olho.<br>Se acha que não, fala com a gente. Mas, enquanto isso, toma esse timeout de '+str(Gerencial.load().timeout_merda)+' minutos.'})
            # Senha ainda não foi plantada pela CO
            userCA.timeout_until = timezone.now() + timezone.timedelta(minutes=Gerencial.load().timeout_merda)
            userCA.save()
            SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {userCA.user.username} fazendo merda, tentaram a senha {request_body["senha"]}, que ainda não foi plantada')
            return render(request, './fila/validarPistaResposta.html', {'senha': senha_testada, 'resposta': 'Você tá errado!', 'context': 'Você tá fazendo merda, e estamos de olho.<br>Se acha que não, fala com a gente. Mas, enquanto isso, toma esse timeout de '+str(Gerencial.load().timeout_merda)+' minutos.'})
        else:
            # Caso senha não exista: Typo ou Brute
            userCA.timeout_until = timezone.now() + timezone.timedelta(minutes=Gerencial.load().timeout_typo)
            userCA.save()
            return render(request, './fila/validarPistaResposta.html', {'senha': senha_testada, 'resposta': 'Pista Não Encontrada','context': 'Você digitou a senha errada.<br>Aguarde o timeout de '+str(Gerencial.load().timeout_typo)+' minutos para tentar novamente'})
