from django import forms
from .models import Artefato
from bootstrap_modal_forms.forms import BSModalModelForm


class ArtefatoForm(BSModalModelForm):
    class Meta:
        model = Artefato
        exclude = []
        widgets = {
            'hora_ativo': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
        }

    def __init__(self, *args, **kwargs):
        super(ArtefatoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
