from django.shortcuts import render
from django.utils import timezone
from caminhos.models import Caminho
from users.models import UserCA
from .models import Gerencial, WebSiteLock
from .forms import WebSiteLockForm,TimeoutForm,GerencialForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalFormView

class WebSiteLockCreateView(IsCOMixin, BSModalCreateView):
    template_name = './gerencial/lockCRUD/createLock.html'
    form_class = WebSiteLockForm
    success_message = 'Success: Lock was created.'
    success_url = reverse_lazy('gerencial:gerencial')

class WebSiteLockEditView(IsCOMixin, BSModalUpdateView):
    model = WebSiteLock
    template_name = './gerencial/lockCRUD/updateLock.html'
    form_class = WebSiteLockForm
    success_message = 'Success: Lock was updated.'
    success_url = reverse_lazy('gerencial:gerencial')

class WebSiteLockDeleteView(IsCOMixin, BSModalDeleteView):
    model = WebSiteLock
    template_name = './gerencial/lockCRUD/deleteLock.html'
    success_message = 'Success: Lock was deleted.'
    success_url = reverse_lazy('gerencial:gerencial')

class GerencialEditView(IsCOMixin, BSModalUpdateView):
    model = Gerencial
    template_name = './gerencial/updateGerencial.html'
    form_class = GerencialForm
    success_message = 'Success: Gerencial was updated.'
    success_url = reverse_lazy('gerencial:gerencial')

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def editTimeout(request):
    try:
        ca = request.POST['ca']
        timeout = request.POST['timeout']
        ca = UserCA.objects.get(user__username=ca)
        setattr(ca, timeout, timezone.now())
        ca.save()
        return HttpResponse(status=204)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def ViewGerencial(request):
    locks = WebSiteLock.objects.all().order_by('-start_time')
    cas = (x for x in UserCA.objects.all() if x.is_radio)
    context = {'locks':locks, 'cas':cas, 'now':timezone.now()}
    return render(request, './gerencial/viewGerencial.html',context)

@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def startCaca(request):
    try:
        ge = Gerencial.load()
        ge.caca_start = not ge.caca_start
        ge.save()
        return HttpResponse(status=204)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

class CreateTimeoutView(IsCOMixin, BSModalFormView):
    template_name = 'gerencial/timeoutForm.html'
    form_class = TimeoutForm

    def form_valid(self, form):
        self.user = form.cleaned_data['user']
        self.type = form.cleaned_data['type']
        self.time = form.cleaned_data['time']
        ca = UserCA.objects.get(pk=self.user)
        setattr(ca, self.type, timezone.now()+ timezone.timedelta(hours=self.time.hour, minutes=self.time.minute))
        ca.save()
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('gerencial:gerencial')
