from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from estoque.dados_modelo import SECOES, linhas_da_secao
from estoque.models import Produto, Secao


class Command(BaseCommand):
    help = "Carrega (ou atualiza) as seções e os produtos do modelo físico."

    @transaction.atomic
    def handle(self, *args, **opts):
        ordem_secao = {}
        total = 0
        for titulo, pagina, coluna, valor_padrao, texto in SECOES:
            chave = (pagina, coluna)
            ordem_secao[chave] = ordem_secao.get(chave, 0) + 1
            secao, _ = Secao.objects.update_or_create(
                pagina=pagina, coluna=coluna, ordem=ordem_secao[chave],
                defaults={"titulo": titulo},
            )
            for ordem, (codigo, nome, valor) in enumerate(linhas_da_secao(valor_padrao, texto), 1):
                Produto.objects.update_or_create(
                    codigo=codigo,
                    defaults={"secao": secao, "nome": nome,
                              "valor_unit": Decimal(valor), "ordem": ordem},
                )
                total += 1
        self.stdout.write(self.style.SUCCESS(f"{total} produtos carregados."))
