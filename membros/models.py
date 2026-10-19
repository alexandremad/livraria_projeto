from django.db import models
import io

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

class Membro(models.Model):
    # Opções de Seleção
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Solteiro(a)'),
        ('C', 'Casado(a)'),
        ('V', 'Viúvo(a)'),
        ('D', 'Divorciado(a)'),
    ]

    FUNCAO_CHOICES = [
        ('membro', 'Membro(a)'),
        ('cooperador', 'Cooperador(a)'),
        ('diacono', 'Diácono'),
        ('obreiro', 'Obreiro(a)'),
        ('presbitero', 'Presbítero'),
        ('pastor', 'Pastor'),
        ('2_pastor', '2º Pastor'),
    ]

    # Dados Pessoais
    nome = models.CharField("Nome", max_length=150)
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO_CHOICES)
    
    # Campo de Foto 3x4 Adicionado Aqui:
    foto = models.ImageField("Foto 3x4", upload_to='fotos_membros/', blank=True, null=True)
    
    estado_civil = models.CharField("Estado Civil", max_length=1, choices=ESTADO_CIVIL_CHOICES)
    data_nascimento = models.DateField("Data de Nascimento")
    naturalidade = models.CharField("Naturalidade", max_length=100)
    nacionalidade = models.CharField("Nacionalidade", max_length=100, default="Brasileira")
    profissao = models.CharField("Profissão", max_length=100, blank=True, null=True)
    rg = models.CharField("RG", max_length=20)
    cpf = models.CharField("CPF", max_length=14, unique=True)

    # Endereço
    endereco = models.CharField("Endereço", max_length=200)
    numero = models.CharField("Número", max_length=20)
    cep = models.CharField("CEP", max_length=10)
    bairro = models.CharField("Bairro", max_length=100)
    cidade = models.CharField("Cidade", max_length=100)
    estado = models.CharField("Estado", max_length=2)

    # Contactos
    celular = models.CharField("Celular", max_length=20)
    celular_contato = models.CharField("Celular de Contacto", max_length=20, blank=True, null=True)
    nome_contato = models.CharField("Nome do Contacto", max_length=100, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)

    # Família
    nome_pai = models.CharField("Nome do Pai", max_length=150, blank=True, null=True)
    nome_mae = models.CharField("Nome da Mãe", max_length=150, blank=True, null=True)
    nome_conjuge = models.CharField("Nome do Cônjuge", max_length=150, blank=True, null=True)
    data_casamento = models.DateField("Data do Casamento", blank=True, null=True)
    nome_filhos = models.TextField("Nome dos Filhos", blank=True, null=True)
    celular_filho = models.CharField("Celular dos Filhos", max_length=20, blank=True, null=True)

    # Saúde
    possui_doenca = models.BooleanField("Possui alguma doença?", default=False)
    qual_doenca = models.CharField("Qual doença?", max_length=200, blank=True, null=True)

    # Vida Ministerial
    funcao_ministerial = models.CharField("Função Ministerial", max_length=50, choices=FUNCAO_CHOICES, blank=True, null=True)
    data_batismo = models.DateField("Data de Batismo", blank=True, null=True)
    lider_departamento = models.BooleanField("Líder de Departamento?", default=False)
    qual_departamento = models.CharField("Qual Departamento?", max_length=100, blank=True, null=True)

    # Disponibilidade
    dias_culto = models.CharField("Dias que vem ao culto", max_length=200, blank=True, null=True)
    periodo_apoio = models.TextField("Melhor dia e período para apoiar em escalas", blank=True, null=True)
    observacoes = models.TextField("Observações", blank=True, null=True)

    # Anexos (Documentos Xerox/Cópia)
    doc_cpf_rg = models.FileField("CPF e RG (Cópia)", upload_to='documentos/cpf_rg/', blank=True, null=True)
    doc_comprovante_residencia = models.FileField("Comprovante de Endereço", upload_to='documentos/enderecos/', blank=True, null=True)
    doc_certidao_nascimento = models.FileField("Certidão de Nascimento", upload_to='documentos/certidoes/', blank=True, null=True)
    doc_certidao_casamento = models.FileField("Certidão de Casamento", upload_to='documentos/certidoes/', blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.cpf}"