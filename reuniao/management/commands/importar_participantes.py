import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from reuniao.models import Participante


class Command(BaseCommand):
    help = ("Importa participantes de um CSV exportado do MySQL/phpMyAdmin. "
            "Colunas: nome, setor e (opcional) data_cadastro. Pode rodar de novo sem duplicar.")

    def add_arguments(self, parser):
        parser.add_argument("arquivo", help="caminho do arquivo .csv")

    def handle(self, *args, **opts):
        try:
            f = open(opts["arquivo"], newline="", encoding="utf-8-sig")
        except OSError as e:
            raise CommandError(f"Não consegui abrir o arquivo: {e}")
        with f:
            primeira = f.readline()
            f.seek(0)
            delimitador = ";" if primeira.count(";") > primeira.count(",") else ","
            leitor = csv.DictReader(f, delimiter=delimitador)
            leitor.fieldnames = [(c or "").strip().lower() for c in (leitor.fieldnames or [])]
            if "nome" not in leitor.fieldnames or "setor" not in leitor.fieldnames:
                raise CommandError("O CSV precisa ter as colunas 'nome' e 'setor' na primeira linha.")

            novos = repetidos = sem_data = 0
            for linha in leitor:
                nome = (linha.get("nome") or "").strip()[:100]
                setor = (linha.get("setor") or "").strip()[:50]
                if not nome:
                    continue
                texto_data = (linha.get("data_cadastro") or "").strip()
                try:
                    data = datetime.datetime.fromisoformat(texto_data)
                    if timezone.is_naive(data):
                        data = timezone.make_aware(data)  # horário de Brasília, como no MySQL
                except ValueError:
                    data = timezone.now()
                    sem_data += 1
                _, criado = Participante.objects.get_or_create(nome=nome, setor=setor, data_cadastro=data)
                novos += criado
                repetidos += (not criado)
        self.stdout.write(self.style.SUCCESS(
            f"{novos} importado(s); {repetidos} já existia(m)."))
        if sem_data:
            self.stdout.write(self.style.WARNING(
                f"{sem_data} linha(s) sem data válida ficaram com a data/hora de agora."))
