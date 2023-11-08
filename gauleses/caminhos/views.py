from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Caminho, Corte
from .forms import CaminhoForm, CorteForm
from users.models import UserCA
from django.urls import reverse_lazy
from users.views import CA_check, CO_check, IsCOMixin
from artefatos.models import Artefato
from django.contrib.auth.decorators import login_required, user_passes_test
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from pistas.models import Pista, Senha, PistaLog
from fila.models import Fila


class CaminhoCreateView(IsCOMixin, BSModalCreateView):
    template_name = './caminhos/caminhoCRUD/createCaminho.html'
    form_class = CaminhoForm
    success_message = 'Sucesso: Caminho foi criado.'
    success_url = reverse_lazy('caminhos:allCaminhos')


class CaminhoEditView(IsCOMixin, BSModalUpdateView):
    model = Caminho
    template_name = './caminhos/caminhoCRUD/updateCaminho.html'
    form_class = CaminhoForm
    success_message = 'Sucesso: Caminho foi atualizado.'
    success_url = reverse_lazy('caminhos:allCaminhos')

    def form_valid(self, form):
        form.instance.last_modified_by = str(self.request.user)
        response = super().form_valid(form)
        return response


class CaminhoDeleteView(IsCOMixin, BSModalDeleteView):
    model = Caminho
    template_name = './caminhos/caminhoCRUD/deleteCaminho.html'
    success_message = 'Sucesso: Caminho foi apagado.'
    success_url = reverse_lazy('caminhos:allCaminhos')


class CaminhoReadView(IsCOMixin, BSModalReadView):
    model = Caminho
    template_name = './caminhos/caminhoCRUD/detailCaminho.html'


class CorteCreateView(IsCOMixin, BSModalCreateView):
    template_name = './caminhos/corteCRUD/createCorte.html'
    form_class = CorteForm
    success_message = 'Sucesso: Corte foi criado.'
    success_url = reverse_lazy('caminhos:allCortes')


class CorteDeleteView(IsCOMixin, BSModalDeleteView):
    model = Corte
    template_name = './caminhos/corteCRUD/deleteCorte.html'
    success_message = 'Sucesso: Corte foi apagado.'
    success_url = reverse_lazy('caminhos:allCortes')


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_cortes(request):
    cortes = Corte.objects.all()
    context = {'cortes': cortes}
    return render(request, './caminhos/viewCortes.html', context)


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_caminhos(request):
    caminhos = Caminho.objects.all()
    context = {'caminhos': caminhos}
    return render(request, './caminhos/viewCaminhos.html', context)

@login_required
def caca_dashboard(request):
    if request.user.is_CO and request.user.is_authenticated:
        allPistaLogs = PistaLog.objects.all().order_by('-timestamp')[:100]
        caminhos = Caminho.objects.all()
        caminhos = sorted(caminhos, key=lambda d: -d.progresso)
        pistas_vivas = [caminho.pista_viva for caminho in Caminho.objects.filter(ativo=True) if caminho.pista_viva]
        alerta = []

        for pista in pistas_vivas:
            for hora_dica in pista.horas_dica:
                if hora_dica > timezone.now():
                    dMin = (hora_dica-timezone.now()).total_seconds()
                    grav = 2
                    if dMin > 60*60: grav = 0
                    elif dMin > 60*30: grav = 1
                    alerta.append({ 'numero':pista.numero,'tipo':'Dica da pista às '+timezone.localtime(hora_dica).strftime("%H:%M"), 'equipe':pista.caminho.CA_ativo, "gravidade":grav })
        print(alerta)
        context = {'caminhos': caminhos, 'allPistaLogs': allPistaLogs, 'alerta': alerta}
        return render(request, './caminhos/cacaDash.html', context)

    elif request.user.is_CA and request.user.is_authenticated:
        radio_user = request.user.userca.radio
        caminhos = [c for c in Caminho.objects.filter(CA_ativo=radio_user)] + [c for c in Caminho.objects.filter(CA_ativo__isnull=True, ativo=True)]
        caminhos = sorted(caminhos, key=lambda caminho: caminho.progresso)
        pistas_vivas = []
        cortado = False
        for caminho in caminhos:
            if not caminho.ativo:
                cortado = True
            else:
                pistas_vivas.append(caminho.pista_viva)

        context = {'caminhos': caminhos,
                   'pistas_vivas': pistas_vivas,
                   'cortado': cortado,
                   'agora': timezone.now()
                   }
        return render(request, './caminhos/cacaDashCA.html', context)
    else:
        return reverse_lazy('login')
