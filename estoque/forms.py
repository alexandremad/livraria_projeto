import datetime

from django import forms

from .models import CAMPOS_CABECALHO, Livraria, Relatorio


class LivrariaForm(forms.ModelForm):
    class Meta:
        model = Livraria
        fields = ["nome", "principal", "ativa"] + CAMPOS_CABECALHO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # uma livraria não pode ser auxiliar de si mesma
        if self.instance.pk:
            self.fields["principal"].queryset = self.fields["principal"].queryset.exclude(pk=self.instance.pk)


class CabecalhoRelatorioForm(forms.ModelForm):
    """Valida/salva só o cabeçalho do papel (os campos vêm digitados na folha)."""
    class Meta:
        model = Relatorio
        fields = CAMPOS_CABECALHO


class NovoRelatorioForm(forms.Form):
    livraria = forms.ModelChoiceField(queryset=Livraria.objects.filter(ativa=True), label="Livraria")
    mes = forms.CharField(
        label="Referente a",
        widget=forms.DateInput(attrs={"type": "month"}, format="%Y-%m"),
        initial=lambda: datetime.date.today().strftime("%Y-%m"),
    )

    def clean_mes(self):
        valor = self.cleaned_data["mes"]
        try:
            ano, mes = valor.split("-")
            return datetime.date(int(ano), int(mes), 1)
        except (ValueError, TypeError):
            raise forms.ValidationError("Informe mês e ano válidos.")

    def clean(self):
        dados = super().clean()
        livraria, mes = dados.get("livraria"), dados.get("mes")
        if livraria and mes and Relatorio.objects.filter(livraria=livraria, referencia=mes).exists():
            raise forms.ValidationError("Já existe relatório desta livraria para este mês.")
        return dados
