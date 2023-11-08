from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User,UserCA
from bootstrap_modal_forms.forms import BSModalModelForm

class CustomUserCreationForm(BSModalModelForm, UserCreationForm):
    is_radio = forms.BooleanField(label="É Radio", required=False)
    radio = forms.ModelChoiceField(queryset=UserCA.objects.filter(is_radio=True), empty_label="Nenhum", required=False)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'is_CA', 'is_CO']
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if not visible.field.widget.input_type == 'checkbox':
                visible.field.widget.attrs['class'] = 'form-control'
            else:
                visible.field.widget.attrs['class'] = 'form-check-input'
            
class UserEditForm(BSModalModelForm):
    is_radio = forms.BooleanField(label="É Radio", required=False)
    radio = forms.ModelChoiceField(queryset=UserCA.objects.filter(is_radio=True), empty_label="Nenhum", required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'is_CA', 'is_CO']
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if not visible.field.widget.input_type == 'checkbox':
                visible.field.widget.attrs['class'] = 'form-control'
            else:
                visible.field.widget.attrs['class'] = 'form-check-input'
        inst = kwargs.pop('instance', None)
        if inst.is_CA:
            self.fields['is_radio'].initial = inst.userca.is_radio
            print(inst.userca.radio)
            self.fields['radio'].initial = inst.userca.radio
