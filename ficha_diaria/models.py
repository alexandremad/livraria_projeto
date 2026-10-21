from django.db import models


class FichaDiaria(models.Model):
    """Ficha diária (abertura do cofre) ligada a um relatório mensal da livraria."""
    relatorio = models.OneToOneField(
        "estoque.Relatorio", on_delete=models.CASCADE, related_name="ficha_diaria"
    )
    observacoes = models.TextField("Observações", blank=True)  # uma linha do papel por linha de texto
    valor_total = models.DecimalField(
        "Valor total em relatório", max_digits=12, decimal_places=2, null=True, blank=True
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ficha diária"
        verbose_name_plural = "Fichas diárias"

    def __str__(self):
        return f"Ficha diária - {self.relatorio}"


class FichaDiariaLinha(models.Model):
    ficha = models.ForeignKey(FichaDiaria, on_delete=models.CASCADE, related_name="linhas")
    posicao = models.PositiveSmallIntegerField()
    data_abertura = models.CharField("Data de abertura do cofre", max_length=20, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    testemunha_1 = models.CharField("Testemunha 1", max_length=100, blank=True)
    testemunha_2 = models.CharField("Testemunha 2", max_length=100, blank=True)
    testemunha_3 = models.CharField("Testemunha 3", max_length=100, blank=True)
    testemunha_4 = models.CharField("Testemunha 4", max_length=100, blank=True)
    testemunha_5 = models.CharField("Testemunha 5", max_length=100, blank=True)

    class Meta:
        ordering = ["posicao"]
        unique_together = [("ficha", "posicao")]

    def __str__(self):
        return f"{self.ficha} - linha {self.posicao}"
