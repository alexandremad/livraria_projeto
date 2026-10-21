"""
Tratamento de numeros no cadastro de membros: CPF, RG e telefones.

- O que o usuario digita e limpo: so ficam os numeros (o banco guarda SOMENTE numeros).
- Na tela, o JavaScript (static/membros/js/mascaras.js) bloqueia letras e coloca a mascara
  (CPF 000.000.000-00 e telefone (00) 00000-0000) sem o usuario digitar pontos ou tracos.
"""
import re

from django.core.exceptions import ValidationError

# --- Ajustes (mude aqui se precisar) -------------------------------------------------
VALIDAR_DIGITOS_CPF = False      # True = recusa CPF com digitos verificadores invalidos
TELEFONE_TAMANHOS = (10, 11)     # DDD + numero: 10 (fixo) ou 11 (celular)
RG_MIN, RG_MAX = 5, 15           # quantidade de numeros aceita no RG
# ---------------------------------------------------------------------------------------


def so_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf):
    """Confere os dois digitos verificadores do CPF (somente numeros, 11 posicoes)."""
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(cpf[n]) * (i + 1 - n) for n in range(i))
        if (soma * 10) % 11 % 10 != int(cpf[i]):
            return False
    return True


# atributos HTML que o JavaScript usa para colocar a mascara
_ATRIBUTOS = {
    "cpf": {"data-mascara": "cpf", "maxlength": 14, "placeholder": "000.000.000-00"},
    "rg": {"data-mascara": "numeros", "maxlength": RG_MAX, "placeholder": "Somente números"},
    "celular": {"data-mascara": "tel", "maxlength": 15, "placeholder": "(00) 00000-0000"},
    "celular_contato": {"data-mascara": "tel", "maxlength": 15, "placeholder": "(00) 00000-0000"},
    "celular_filho": {"data-mascara": "tel", "maxlength": 15, "placeholder": "(00) 00000-0000"},
}


class SomenteNumerosMixin:
    """Use antes de forms.ModelForm: class MembroForm(SomenteNumerosMixin, forms.ModelForm)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome, atributos in _ATRIBUTOS.items():
            if nome in self.fields:
                self.fields[nome].widget.attrs.update(
                    {"inputmode": "numeric", "autocomplete": "off", **atributos})

    def clean_cpf(self):
        cpf = so_digitos(self.cleaned_data.get("cpf"))
        if len(cpf) != 11:
            raise ValidationError("O CPF deve ter 11 números.")
        if VALIDAR_DIGITOS_CPF and not cpf_valido(cpf):
            raise ValidationError("CPF inválido. Confira os números digitados.")
        return cpf

    def clean_rg(self):
        rg = so_digitos(self.cleaned_data.get("rg"))
        if not (RG_MIN <= len(rg) <= RG_MAX):
            raise ValidationError(f"O RG deve ter somente números ({RG_MIN} a {RG_MAX} dígitos).")
        return rg

    def _telefone(self, nome):
        original = self.cleaned_data.get(nome)
        numero = so_digitos(original)
        if not numero:
            return original  # vazio: a obrigatoriedade ja e tratada pelo proprio campo
        if len(numero) not in TELEFONE_TAMANHOS:
            raise ValidationError("Informe o DDD e o número do telefone (10 ou 11 números).")
        return numero

    def clean_celular(self):
        return self._telefone("celular")

    def clean_celular_contato(self):
        return self._telefone("celular_contato")

    def clean_celular_filho(self):
        return self._telefone("celular_filho")
