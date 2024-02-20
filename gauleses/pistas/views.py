from django.shortcuts import render
from django.core.files import File
import requests
import mimetypes
from caminhos.models import allCaminhos
from .models import Pista, PistaLog
from .forms import PistaForm, PistaPlantarForm, SenhaBatchForm
from django.urls import reverse_lazy
from users.views import CA_check, CO_check, IsCOMixin
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import user_passes_test
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView,BSModalFormView
from gerencial.models import Gerencial
from gerencial.utils import SendTelegramMessage
from pistas.models import Pista, Senha
from users.models import allRadios
import gspread
import re
import secrets
from difflib import SequenceMatcher


alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


class PistaCreateView(IsCOMixin, BSModalCreateView):
    template_name = './pistas/pistasCRUD/createPista.html'
    form_class = PistaForm
    success_message = 'Sucesso: Pista foi criada.'
    success_url = reverse_lazy('pistas:allPistas')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
    def get_context_data(self, **kwargs):
        context = super(PistaCreateView, self).get_context_data(**kwargs)
        context['senhas'] = Senha.objects.filter(valida=True, queimada=False, pista__isnull=True)        
        return context

class PistaEditView(IsCOMixin, BSModalUpdateView):
    model = Pista
    template_name = './pistas/pistasCRUD/updatePista.html'
    form_class = PistaForm
    success_message = 'Sucesso: Pista foi atualizada.'
    success_url = reverse_lazy('pistas:allPistas')

    def form_valid(self, form):
        form.instance.user_ultima_modificacao = str(self.request.user)
        response = super().form_valid(form)
        return response
    def get_context_data(self, **kwargs):
        context = super(PistaEditView, self).get_context_data(**kwargs)
        context['senhas'] = Senha.objects.filter(valida=True, queimada=False, pista__isnull=True) | Senha.objects.filter(pista=context['object'])
        context['usuarios_possiveis'] = allRadios()
        
        return context
    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        return reverse_lazy('pistas:allPistas')
        
class PistaDeleteView(IsCOMixin, BSModalDeleteView):
    model = Pista
    template_name = './pistas/pistasCRUD/deletePista.html'
    success_message = 'Sucesso: Pista foi deletada.'
    success_url = reverse_lazy('pistas:allPistas')

class PistaReadView(IsCOMixin, BSModalReadView):
    model = Pista
    template_name = './pistas/pistasCRUD/detailPista.html'

class PistaPlantarView(IsCOMixin, BSModalUpdateView):
    model = Pista
    template_name = './pistas/pistasCRUD/plantarPista.html'
    form_class = PistaPlantarForm
    success_message = 'Sucesso: Pista foi plantada.'

    def form_valid(self, form):
        form.instance.last_modified_by = str(self.request.user)
        form.instance.status = 'plantada'
        response = super().form_valid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super(PistaPlantarView, self).get_context_data(**kwargs)
        context['senhas'] = Senha.objects.filter(valida=True, queimada=False, pista__isnull=True)
        return context

    def get_success_url(self):
        try:
            url = self.request.GET.get('next')
        except:
            url = reverse_lazy('pistas:allPistas')
        return url

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_pistas(request):
    pistas = Pista.objects.all().order_by('numero')
    context = {'pistas': pistas}
    return render(request, './pistas/viewPistas.html', context)

@user_passes_test(CA_check, login_url='login', redirect_field_name=None)
def view_pista_CA(request, pk):
    if pk:
        if request.user.is_CA and request.user.is_authenticated:
            radio_user = request.user.userca.radio
            try:
                pesq = Pista.objects.get(id=pk)
            except:
                SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {request.username} fazendo merda, tentando acessar pista no bruteforce')
                raise Http404()

            if not pesq or not (pesq.caminho.CA_ativo == radio_user or pesq.caminho.CA_ativo is None):
                SendTelegramMessage(chat_id=Gerencial.load().telegram_group, message=f'Usuário do {request.username} fazendo merda, tentando acessar pista no bruteforce')
                raise Http404()
            else:
                context = {'pista': pesq}
                return render(request, './pistas/pistaCA.html', context)       
    raise Http404()


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_senhas(request):
    senhas = Senha.objects.all().order_by('-valida', 'queimada')
    context = {'senhas': senhas}
    return render(request, './pistas/viewSenhas.html', context)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def queima_senhas(request):
    try:
        valor = request.POST['valor']
        senha = Senha.objects.get(valor=valor)
        senha.queimada = True
        senha.save()
        return HttpResponse(status=204)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def deletar_senhas(request):
    Senha.objects.all().delete()
    return HttpResponse(status=200)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def generate_senha(senhas_atuais):
    senha = False
    while not senha:
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        for n in senhas_atuais:
            if similar(n,password) < 0.5:
                senha = password
        if not senhas_atuais:
            senha=password
    return senha

class BatchSenhaView(IsCOMixin, BSModalFormView):
    template_name = 'pistas/batchSenhas.html'
    form_class = SenhaBatchForm

    def form_valid(self, form):
        self.quantidade = form.cleaned_data['quantidade']
        self.validas = form.cleaned_data['validas']
        senhas_atuais = list(Senha.objects.all().values_list('valor', flat=True))
        for _ in range(self.quantidade):
            ns = generate_senha(senhas_atuais)
            Senha(valor=ns, valida=self.validas).save()
            senhas_atuais.append(ns)
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('pistas:allSenhas')

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def resetar_pistas(request):
    Pista.objects.all().update(status='nao_plantada')
    Pista.objects.all().update(old_status='nao_plantada')
    Pista.objects.all().update(senha=None)
    Pista.objects.all().update(old_senha=None)
    Pista.objects.all().update(hora_recolhida=None)
    Pista.objects.all().update(hora_inicio=None)
    Pista.objects.all().update(caminho=None)    
    PistaLog.objects.all().delete()

    return HttpResponse(status=200)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def deletar_pistas(request):
    Pista.objects.all().delete()
    PistaLog.objects.all().delete()
    return HttpResponse(status=200)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def todas_senhas(request):
    sv= Senha.objects.filter(valida=True, queimada=False)
    snv= Senha.objects.filter(valida=False)
    return render(request, 'pistas/todasSenhas.html', context={'senhas_validas':sv, 'senhas_invalidas':snv})

def xstr(s):
    return '' if s is None else str(s)

# carrega pistas a partir da planilha de pistas
@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def carregar_pistas(request):
    if request.method == 'GET':
        return render(request, './pistas/pistasCRUD/carregarPistasForm.html')

    url = request.POST['link']
    print(url)
    gcId, sheetId = re.findall(r'\/d\/(.+)\/.+gid=(.+)', url)[0]

    try:
        gc = gspread.service_account(filename='mmc-2023-920e16e15c52.json')
        print(type(gc))
    except Exception as e:
        print(e)
        return render(request, './pistas/pistasCRUD/carregarPistasResponse.html', context={'erro':"Erro ao acessar arquivo de credenciais"})
    try:
        plan = gc.open_by_key(gcId)
        index = [ x.id for x in plan.worksheets() ].index(int(sheetId))
        sheet = plan.get_worksheet(index)
        gen = sheet.get_all_values()[1:]
    except Exception as e:
        print(e)
        return render(request, './pistas/pistasCRUD/carregarPistasResponse.html', context={'erro':"Erro ao acessar planilha"})

    url = gspread.urls.SPREADSHEET_URL % (gcId)
    response = gc.request('get', url, params = {'includeGridData': 'true', 'alt':'json', 'ranges':'B2:B'+str(len(gen)+1)}).json()
    details = response['sheets'][index]['data'][0]['rowData']

    map_columns = {'numero':0,
                    'conteudo':1,
                    'tipo_conteudo':2,
                    'nome_arquivo':3,
                    'link':4,
                    'autor':5,
                    'macro':6,
                    'micro':7,
                    'solucao':8,
                    'observacao':9}

    df = response['properties']['defaultFormat']

    defaultFormat = {'backgroundColor':df['backgroundColor'],
                    'fontFamily': df['textFormat']['fontFamily'].split(',')[0].lower(),
                    'fontSize': df['textFormat']['fontSize'],
                    'bold': df['textFormat']['bold'],
                    'italic': df['textFormat']['italic'],
                    'strikethrough': df['textFormat']['strikethrough'],
                    'underline': df['textFormat']['underline'],
                    'foregroundColorStyle': df['textFormat']['foregroundColorStyle'],
                    'backgroundColorStyle':df['backgroundColorStyle']}

    revisao = []

    for i in range(len(gen)):
        numero = gen[i][map_columns['numero']]
        conteudo = gen[i][map_columns['conteudo']]
        tipo_conteudo = gen[i][map_columns['tipo_conteudo']]
        nome_arquivo = gen[i][map_columns['nome_arquivo']]
        link = gen[i][map_columns['link']]
        autor = gen[i][map_columns['autor']]
        macro = gen[i][map_columns['macro']]
        micro = gen[i][map_columns['micro']]
        solucao = gen[i][map_columns['solucao']]
        observacao = gen[i][map_columns['observacao']] 

        conteudo = xstr(conteudo)
        autor = xstr(autor)
        macro = xstr(macro)
        micro = xstr(micro)
        solucao = xstr(solucao)
        observacao = xstr(observacao)

        cf = details[i]['values'][0]['effectiveFormat']

        cellFormat = {'backgroundColor':cf['backgroundColor'],
                        'fontFamily': cf['textFormat']['fontFamily'].split(',')[0].lower(),
                        'fontSize': cf['textFormat']['fontSize'],
                        'bold': cf['textFormat']['bold'],
                        'italic': cf['textFormat']['italic'],
                        'strikethrough': cf['textFormat']['strikethrough'],
                        'underline': cf['textFormat']['underline'],
                        'foregroundColorStyle': cf['textFormat']['foregroundColorStyle'],
                        'backgroundColorStyle':cf['backgroundColorStyle']}

        formatRun = details[i]['values'][0].get('textFormatRuns')
        doubleSpaced = '  ' in conteudo and not "<pre>" in conteudo

        if cellFormat != defaultFormat or bool(formatRun) or doubleSpaced:
            revisao.append('Revise a pista <b>'+numero+'</b>. É possível que ela tenha formatação na planilha e não esteja como HTML')

        if tipo_conteudo != 'HTML' and tipo_conteudo != 'Texto' and not link:
            revisao.append('Revise a pista <b>'+numero+'</b>. Está faltando o link do arquivo dela')

        if (tipo_conteudo == 'HTML' or tipo_conteudo == 'Texto') and (link or conteudo=='') :
            revisao.append('Revise a pista <b>'+numero+'</b>. Seu tipo está como texto ou HTML, mas possui texto vazio ou link')

        pis = Pista(numero = numero,
              conteudo_texto = conteudo,
              tipo_conteudo = tipo_conteudo,
              autor = autor,
              macro = macro,
              micro = micro,
              solucao = solucao,
              observacao = observacao)

        if link:
            try:
                response = requests.get(link, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
                if not response.ok:
                    raise 'Erro'
                open('temp', 'wb').write(response.content)
                if not nome_arquivo:
                    content_type = response.headers['content-type']
                    extension = mimetypes.guess_extension(content_type)
                    nome_arquivo = 'Pista_'+str(numero)+extension
                pis.arquivo.save(nome_arquivo, File(open('temp', 'rb')))
            except:
                revisao.append('Revise a pista <b>'+numero+'</b>. Houve um problema em carregar seu arquivo')

        try:
            pis.save()
            pis.caminhos_possiveis.set(allCaminhos())
            pis.usuarios_possiveis.set(allRadios())
            
            pis.save()
        except:
            revisao.append('Revise a pista <b>'+numero+'</b>. Erro no salvamento')
    return render(request, './pistas/pistasCRUD/carregarPistasResponse.html', context={'revisao':revisao})