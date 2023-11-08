from .forms import UserEditForm, CustomUserCreationForm
from django.shortcuts import redirect, render
from django.contrib.sessions.models import Session
from django.utils import timezone
from users.models import User
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import views as auth_views
from django.conf import settings
import requests


class IsCOMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            return self.request.user.is_CO
        except:
            return False


def CO_check(user):
    return user.is_CO if not user.is_anonymous else False


def CA_check(user):
    return user.is_CA if not user.is_anonymous else False


def auth_check(user):
    return user.is_authenticated


class MyLoginView(auth_views.LoginView):
    def post(self, form):
        request_body = self.request.POST
        if not request_body:
            return None
        recaptcha_response = request_body['g-recaptcha-response']
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        if result['success']:
            return super().post(form)
        else:
            # avisar que o captcha deu errado
            return redirect('login')


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def sessions(request):
    # Quero carregar todos usuarios, aqueles que sessao ativa e nao tem e poder deslogar quem ta ativo
    # mostrar o ultimo login de todos
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    users = User.objects.all()

    userContext = []

    for user in users:
        userContext.append({"user":user, "logado":False, 'sessId':''})

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        if not data.get('_password_reset_token', False) and data:
            sId = int(data.get('_auth_user_id', None))
            n = next((i for i, item in enumerate(userContext) if item["user"].id == sId), -1)
            if n>-1:
                if userContext[n]["logado"] == False:
                    userContext[n]["sessId"] = session.session_key
                    userContext[n]["logado"] = True
                else:
                    userContext.append({"user":userContext[n]['user'], "logado":True, 'sessId':session.session_key})
    
    context = {'userContext':userContext}
    print(userContext)
    return render(request, "./users/sessions.html", context)



class SessionDeleteView(IsCOMixin, BSModalDeleteView):
    model = Session
    template_name = './users/deleteSession.html'
    success_message = 'Sucesso: Session foi apagada.'
    success_url = reverse_lazy('sessions')


class UserEditView(IsCOMixin, BSModalUpdateView):
    model = User
    template_name = './users/usersCRUD/updateUser.html'
    form_class = UserEditForm
    success_message = 'Success: User was updated.'
    success_url = reverse_lazy('sessions')
    def form_valid(self, form):
        is_radio = form.cleaned_data['is_radio']
        radio = form.cleaned_data['radio']
        print(is_radio, radio)
        form.instance.is_radio = is_radio
        form.instance.radio = radio
        response = super().form_valid(form)
        return response


class UserDeleteView(IsCOMixin, BSModalDeleteView):
    model = User
    template_name = './users/usersCRUD/deleteUser.html'
    success_message = 'Success: User was deleted.'
    success_url = reverse_lazy('sessions')

class UserReadView(IsCOMixin, BSModalReadView):
    model = User
    template_name = './users/usersCRUD/detailUser.html'

class UserCreateView(IsCOMixin, BSModalCreateView):
    template_name = './users/usersCRUD/createUser.html'
    form_class = CustomUserCreationForm
    success_message = 'Success: User was created.'
    success_url = reverse_lazy('sessions')
    def form_valid(self, form):
        is_radio = form.cleaned_data['is_radio']
        radio = form.cleaned_data['radio']
        form.instance.is_radio = is_radio
        form.instance.radio = radio
        response = super().form_valid(form)
        return response

# TODO: Batch de usuários?