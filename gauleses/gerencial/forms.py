from django import forms

from users.models import UserCA
from .models import WebSiteLock, Gerencial
from bootstrap_modal_forms.forms import BSModalModelForm,BSModalForm

class WebSiteLockForm(BSModalModelForm):
    class Meta:
        model = WebSiteLock
        exclude = []
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
        }

    def __init__(self, *args, **kwargs):
        super(WebSiteLockForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class GerencialForm(BSModalModelForm):
    class Meta:
        model = Gerencial
        exclude = ['_old_caca_start', 'caca_start']
    def __init__(self, *args, **kwargs):
        super(GerencialForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

def userChoices():
    return ((x.pk, x.ca_short) for x in UserCA.objects.all() if x.is_radio)

class TimeoutForm(BSModalForm):
    user = forms.ChoiceField(choices=userChoices, label='Usuário')
    type = forms.ChoiceField(choices=[('timeout_until', 'Pistas'), ('timeout_artefato', 'Artefatos')], label='Tipo')
    time = forms.TimeField(label='Tempo')

    class Meta:
        fields = ['user', 'type', 'time']

    def __init__(self, *args, **kwargs):
        super(TimeoutForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'