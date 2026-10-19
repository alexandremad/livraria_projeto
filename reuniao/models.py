from django.db import models
from django.utils import timezone


class Participante(models.Model):
    # equivale à tabela `participantes` do MySQL (id, nome, setor, data_cadastro)
    nome = models.CharField("Nome completo", max_length=100)
    setor = models.CharField("Setor", max_length=50)
    # default (e não auto_now_add) para permitir importar a data original dos registros antigos
    data_cadastro = models.DateTimeField("Cadastrado em", default=timezone.now)

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        ordering = ["-data_cadastro"]

    def __str__(self):
        return f"{self.nome} ({self.setor})"
