from django import forms
from .models import Desejo
from bootstrap_modal_forms.forms import BSModalModelForm


class DesejoForm(BSModalModelForm):
    class Meta:
        model = Desejo
        exclude = []
        widgets = {
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
            'end_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class': 'datetimefield'}),
        }

    def __init__(self, *args, **kwargs):
        super(DesejoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
