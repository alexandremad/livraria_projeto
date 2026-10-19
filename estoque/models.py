from decimal import Decimal

from django.db import models

from .constantes import LINHAS_LIVRES

PORTES = [
    ("ESTADUAL", "Estadual"),
    ("SETORIAL", "Setorial"),
    ("CENTRAL", "Central"),
    ("REGIONAL", "Regional"),
    ("LOCAL", "Local"),
]

CAMPOS_CABECALHO = [
    "estadual_responsavel", "porte", "cep", "rua", "numero", "bairro", "cidade", "uf",
    "cod_totvs", "dirigente", "dirigente_tel", "dirigente_email",
    "vol_estoque", "vol_estoque_tel", "vol_estoque_email",
    "vol_financeiro", "vol_financeiro_tel", "vol_financeiro_email",
]


class DadosCabecalho(models.Model):
    """Campos do cabeçalho do papel. Usado na Livraria e copiado para cada Relatório."""
    estadual_responsavel = models.CharField("Estadual responsável", max_length=120, blank=True)
    porte = models.CharField("Porte", max_length=10, choices=PORTES, blank=True)
    cep = models.CharField("CEP", max_length=9, blank=True)
    rua = models.CharField("Rua / Av.", max_length=150, blank=True)
    numero = models.CharField("Nº", max_length=10, blank=True)
    bairro = models.CharField("Bairro", max_length=80, blank=True)
    cidade = models.CharField("Cidade", max_length=80, blank=True)
    uf = models.CharField("UF", max_length=2, blank=True)
    cod_totvs = models.CharField("Cód. TOTVS", max_length=30, blank=True)
    dirigente = models.CharField("Dirigente", max_length=120, blank=True)
    dirigente_tel = models.CharField("Tel. dirigente", max_length=30, blank=True)
    dirigente_email = models.CharField("E-mail dirigente", max_length=120, blank=True)
    vol_estoque = models.CharField("Vol. estoque livraria", max_length=120, blank=True)
    vol_estoque_tel = models.CharField("Tel. vol. estoque", max_length=30, blank=True)
    vol_estoque_email = models.CharField("E-mail vol. estoque", max_length=120, blank=True)
    vol_financeiro = models.CharField("Vol. financeira", max_length=120, blank=True)
    vol_financeiro_tel = models.CharField("Tel. vol. financeira", max_length=30, blank=True)
    vol_financeiro_email = models.CharField("E-mail vol. financeira", max_length=120, blank=True)

    class Meta:
        abstract = True


class Livraria(DadosCabecalho):
    """Livraria principal ou auxiliar."""
    nome = models.CharField("Nome da livraria", max_length=150)
    principal = models.ForeignKey(
        "self", verbose_name="Livraria principal (se for auxiliar)",
        null=True, blank=True, on_delete=models.PROTECT, related_name="auxiliares",
        limit_choices_to={"principal__isnull": True},
    )
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Livraria"
        verbose_name_plural = "Livrarias"

    def __str__(self):
        return f"{self.nome} (auxiliar)" if self.principal_id else self.nome

    @property
    def eh_auxiliar(self):
        return self.principal_id is not None


class Secao(models.Model):
    """Bloco do papel (ex.: BÍBLIAS, VESTUÁRIO, CDs ORAÇÃO) com posição fixa na folha."""
    titulo = models.CharField(max_length=60)
    pagina = models.PositiveSmallIntegerField()
    coluna = models.PositiveSmallIntegerField()
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["pagina", "coluna", "ordem"]
        unique_together = [("pagina", "coluna", "ordem")]
        verbose_name = "Seção"
        verbose_name_plural = "Seções"

    def __str__(self):
        return f"p{self.pagina}/c{self.coluna} - {self.titulo}"


class Produto(models.Model):
    secao = models.ForeignKey(Secao, on_delete=models.CASCADE, related_name="produtos")
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=120)
    valor_unit = models.DecimalField("Valor unit. (R$)", max_digits=8, decimal_places=2)
    ordem = models.PositiveSmallIntegerField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["secao__pagina", "secao__coluna", "secao__ordem", "ordem"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Relatorio(DadosCabecalho):
    livraria = models.ForeignKey(Livraria, on_delete=models.PROTECT, related_name="relatorios")
    referencia = models.DateField("Referente a (mês/ano)", help_text="Sempre o dia 1 do mês")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-referencia", "livraria__nome"]
        unique_together = [("livraria", "referencia")]

    def __str__(self):
        return f"{self.livraria.nome} - {self.referencia:%m/%Y}"

    def preencher_cabecalho_da_livraria(self):
        for campo in CAMPOS_CABECALHO:
            setattr(self, campo, getattr(self.livraria, campo))

    def criar_linhas(self):
        """Cria todas as linhas do papel: produtos (com valor do dia) e linhas livres."""
        itens = [
            ItemRelatorio(relatorio=self, produto=p, valor_unit=p.valor_unit)
            for p in Produto.objects.filter(ativo=True)
        ]
        ItemRelatorio.objects.bulk_create(itens)
        livres = []
        for (pagina, coluna), cfg in LINHAS_LIVRES.items():
            for pos in range(1, cfg["qtd"] + 1):
                livres.append(LinhaLivre(relatorio=self, pagina=pagina, coluna=coluna, posicao=pos))
        LinhaLivre.objects.bulk_create(livres)


class _Quantidades(models.Model):
    estoque_inicial = models.IntegerField("Estoque inicial", null=True, blank=True)
    entrada = models.IntegerField("Entrada", null=True, blank=True)
    transferencia = models.IntegerField("Transferência", null=True, blank=True)
    qtd_vendas = models.IntegerField("Qtd. de vendas", null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def custo_total(self):
        if self.qtd_vendas is None or self.valor_unit is None:
            return None
        return Decimal(self.qtd_vendas) * self.valor_unit


class ItemRelatorio(_Quantidades):
    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    valor_unit = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = [("relatorio", "produto")]


class LinhaLivre(_Quantidades):
    """Linhas em branco do papel (novos itens): código, nome e valor são digitados."""
    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, related_name="linhas_livres")
    pagina = models.PositiveSmallIntegerField()
    coluna = models.PositiveSmallIntegerField()
    posicao = models.PositiveSmallIntegerField()
    codigo = models.CharField(max_length=10, blank=True)
    nome = models.CharField(max_length=120, blank=True)
    valor_unit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["pagina", "coluna", "posicao"]
