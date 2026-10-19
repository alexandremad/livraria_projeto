from django import forms

from .models import Participante
from .regioes import REGIOES


class ParticipanteForm(forms.ModelForm):
    # lista de regiões do script original; o banco continua guardando o texto (CharField)
    setor = forms.ChoiceField(
        label="Região",
        choices=[("", "Selecione a Região")] + [(r, r) for r in REGIOES],
    )

    class Meta:
        model = Participante
        fields = ["nome", "setor"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Nome Completo", "autofocus": True}),
        }
