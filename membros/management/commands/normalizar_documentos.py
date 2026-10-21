import re

from django.core.management.base import BaseCommand
from django.db import transaction

from membros.models import Membro

CAMPOS = ["cpf", "rg", "celular", "celular_contato", "celular_filho"]


def _digitos(valor):
    return re.sub(r"\D", "", valor or "")


class Command(BaseCommand):
    help = ("Deixa somente numeros em CPF, RG e telefones dos membros ja cadastrados. "
            "Use --simular para apenas ver o que seria feito.")

    def add_arguments(self, parser):
        parser.add_argument("--simular", action="store_true", help="nao grava nada")

    @transaction.atomic
    def handle(self, *args, **opts):
        membros = list(Membro.objects.all())

        # CPFs que ficariam repetidos depois de tirar pontos e tracos
        por_cpf = {}
        for m in membros:
            por_cpf.setdefault(_digitos(m.cpf), []).append(m.pk)
        repetidos = {k: v for k, v in por_cpf.items() if len(v) > 1}
        ids_conflito = {pk for ids in repetidos.values() for pk in ids}

        ajustados, tamanho_cpf = 0, []
        for m in membros:
            novos = {}
            for campo in CAMPOS:
                antigo = getattr(m, campo)
                if antigo is None:
                    continue
                if campo == "cpf" and m.pk in ids_conflito:
                    continue
                numero = _digitos(antigo)
                if numero != antigo:
                    novos[campo] = numero
            if len(_digitos(m.cpf)) != 11:
                tamanho_cpf.append(m.pk)
            if novos:
                ajustados += 1
                if not opts["simular"]:
                    Membro.objects.filter(pk=m.pk).update(**novos)

        acao = "seriam ajustados" if opts["simular"] else "ajustados"
        self.stdout.write(self.style.SUCCESS(f"{ajustados} membro(s) {acao}."))
        if repetidos:
            ids = sorted(ids_conflito)
            self.stdout.write(self.style.WARNING(
                f"CPF repetido depois da limpeza nos membros de id {ids}. "
                "O CPF desses membros NAO foi alterado: corrija pelo /admin/."))
        if tamanho_cpf:
            self.stdout.write(self.style.WARNING(
                f"CPF com quantidade de numeros diferente de 11 nos membros de id {sorted(tamanho_cpf)}. "
                "Corrija ao editar o cadastro."))
