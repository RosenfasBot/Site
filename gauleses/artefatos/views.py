from django.shortcuts import render, redirect
from .models import Artefato
from .forms import ArtefatoForm
from django.utils import timezone
from users.models import UserCA
import unidecode
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy,reverse
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView

class ArtefatoCreateView(IsCOMixin, BSModalCreateView):
    template_name = './artefatos/artefatoCRUD/createArtefato.html'
    form_class = ArtefatoForm
    success_message = 'Success: Artefato was created.'
    success_url = reverse_lazy('artefatos:allArtefatos')
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class ArtefatoEditView(IsCOMixin, BSModalUpdateView):
    model = Artefato
    template_name = './artefatos/artefatoCRUD/updateArtefato.html'
    form_class = ArtefatoForm
    success_message = 'Success: Artefato was updated.'
    success_url = reverse_lazy('artefatos:allArtefatos')
    def form_valid(self, form):
        form.instance.last_modified_by = str(self.request.user)
        response = super().form_valid(form)
        return response

class ArtefatoDeleteView(IsCOMixin, BSModalDeleteView):
    model = Artefato
    template_name = './artefatos/artefatoCRUD/deleteArtefato.html'
    success_message = 'Success: Artefato was deleted.'
    success_url = reverse_lazy('artefatos:allArtefatos')

class ArtefatoReadView(IsCOMixin, BSModalReadView):
    model = Artefato
    template_name = './artefatos/artefatoCRUD/detailArtefato.html'

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_artefatos(request):
    artefatos = Artefato.objects.all()
    context = {'artefatos':artefatos}
    return render(request, './artefatos/viewArtefatos.html',context)

@user_passes_test(CA_check, login_url='login', redirect_field_name=None)
def artefatoTry(request):
    if request.user.is_CA and request.user.is_authenticated and request.user.userca.p1 and request.method == 'POST':
        request_body = request.POST
        if not request_body:
            raise Http404()
        agora = timezone.now()
        userCA = request.user.userca.radio
        if agora < userCA.timeout_artefato:
            return HttpResponse('erro--timeout')
        gabaTentado = unidecode.unidecode(request_body['senha']).lower().replace(' ', '')
        artefatoAtivo = Artefato.objects.filter(gaba=gabaTentado,hora_ativo__lte=agora, CA_dono__isnull=True)
        if artefatoAtivo:
                return HttpResponse(artefatoAtivo[0].imagemGaba.url)
        else:
            userCA.timeout_artefato = timezone.now() + timezone.timedelta(minutes=2)
            userCA.save()
            return HttpResponse('erro--senha')
    raise Http404