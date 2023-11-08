from django.shortcuts import render
from .models import Desejo
from .forms import DesejoForm
from django.utils import timezone
from django.urls import reverse_lazy
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView


class DesejoCreateView(IsCOMixin, BSModalCreateView):
    template_name = './desejos/desejoCRUD/createDesejo.html'
    form_class = DesejoForm
    success_message = 'Sucesso: Desejo foi criado.'
    success_url = reverse_lazy('desejos:allDesejos')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class DesejoEditView(IsCOMixin, BSModalUpdateView):
    model = Desejo
    template_name = './desejos/desejoCRUD/updateDesejo.html'
    form_class = DesejoForm
    success_message = 'Sucesso: Desejo foi atualizado.'
    success_url = reverse_lazy('desejos:allDesejos')

    def form_valid(self, form):
        print(form.cleaned_data.get('start_time'))
        form.instance.last_modified_by = str(self.request.user)
        response = super().form_valid(form)
        return response


class DesejoDeleteView(IsCOMixin, BSModalDeleteView):
    model = Desejo
    template_name = './desejos/desejoCRUD/deleteDesejo.html'
    success_message = 'Sucesso: Desejo foi apagado.'
    success_url = reverse_lazy('desejos:allDesejos')


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_desejos(request):
    desejos = Desejo.objects.all().order_by('-start_time')
    context = {'desejos': desejos}
    return render(request, './desejos/viewDesejosCO.html', context)


# página de desejos pública
def desejos_page(request):
    desejos = Desejo.objects.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    desejosPast = Desejo.objects.filter(start_time__lt=timezone.now(), end_time__lt=timezone.now()).order_by(
        '-end_time')
    context = {'desejos': desejos, 'desejosPast': desejosPast}
    resp = render(request, './desejos/viewDesejosCA.html', context)
    return resp
