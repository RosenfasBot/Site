from .models import Caminho, Corte
from bootstrap_modal_forms.forms import BSModalModelForm


class CaminhoForm(BSModalModelForm):
    class Meta:
        model = Caminho
        exclude = []

    def __init__(self, *args, **kwargs):
        super(CaminhoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class CorteForm(BSModalModelForm):
    class Meta:
        model = Corte
        exclude = []

    def __init__(self, *args, **kwargs):
        super(CorteForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
