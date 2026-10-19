from django import forms
from .models import Membro

DIAS_SEMANA = [
    ('domingo', 'Domingo'),
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
]

class MembroForm(forms.ModelForm):
    dias_culto_checkboxes = forms.MultipleChoiceField(
        choices=DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Quais dias vem no culto"
    )

    class Meta:
        model = Membro
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_casamento': forms.DateInput(attrs={'type': 'date'}),
            'data_batismo': forms.DateInput(attrs={'type': 'date'}),
            'nome_filhos': forms.Textarea(attrs={'rows': 2}),
            'periodo_apoio': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.dias_culto:
            self.fields['dias_culto_checkboxes'].initial = self.instance.dias_culto.split(',')

    def save(self, commit=True):
        instance = super().save(commit=False)
        dias = self.cleaned_data.get('dias_culto_checkboxes')
        if dias:
            instance.dias_culto = ','.join(dias)
        else:
            instance.dias_culto = ''
        if commit:
            instance.save()
        return instance