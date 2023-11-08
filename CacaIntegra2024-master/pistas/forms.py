from .models import Pista, Senha
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from users.models import UserCA
from bootstrap_modal_forms.forms import BSModalForm

class PistaForm(BSModalModelForm):
    class Meta:
        model = Pista
        exclude = ['old_status', 'old_senha', 'hora_inicio', 'hora_recolhida', 'data_ultima_modificacao', 'user_ultima_modificacao']
        widgets = {
                'conteudo_texto': forms.Textarea(attrs={'rows':4}),
                'solucao': forms.Textarea(attrs={'rows':4}),
                'observacao': forms.Textarea(attrs={'rows':2}),
                }
    def __init__(self, *args, **kwargs):
        super(PistaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['senha'].widget.attrs['list'] = 'senhas'
        self.fields["usuarios_possiveis"].queryset = UserCA.objects.filter(is_radio=True)

class PistaPlantarForm(BSModalModelForm):
    class Meta:
        model = Pista
        fields = ['senha']

    def __init__(self, *args, **kwargs):
        super(PistaPlantarForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['senha'].widget.attrs['list'] = 'senhas'


class SenhaBatchForm(BSModalForm):
    quantidade = forms.IntegerField(label="Quantas senhas você quer gerar?")
    validas = forms.BooleanField(label="Válidas", required=False)

    def __init__(self, *args, **kwargs):
        super(SenhaBatchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name == 'validas':
                visible.field.widget.attrs['class'] = 'form-check-input'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
        self.fields['validas'].initial = True