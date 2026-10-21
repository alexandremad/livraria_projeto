from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from estoque.models import Relatorio

from .conteudo import BANCOS, CONTATO, FAVORECIDO, IGREJA, VERSICULO
from .models import FichaDiaria, FichaDiariaLinha

LINHAS_TABELA = 12        # linhas da tabela de abertura do cofre no papel
LINHAS_OBSERVACOES = 8    # linhas da área "Observações" no papel


def _decimal(texto):
    """Aceita 1234,56 / 1.234,56 / 1234.56."""
    texto = (texto or "").strip().replace(" ", "").replace("R$", "")
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def _obter_ficha(relatorio):
    """Cria a ficha (e as 12 linhas) na primeira vez que é aberta."""
    ficha, _ = FichaDiaria.objects.get_or_create(relatorio=relatorio)
    existentes = set(ficha.linhas.values_list("posicao", flat=True))
    faltam = [FichaDiariaLinha(ficha=ficha, posicao=p)
              for p in range(1, LINHAS_TABELA + 1) if p not in existentes]
    if faltam:
        FichaDiariaLinha.objects.bulk_create(faltam)
    return ficha


def _linhas_observacoes(ficha):
    linhas = ficha.observacoes.split("\n") if ficha.observacoes else []
    linhas = (linhas + [""] * LINHAS_OBSERVACOES)[:LINHAS_OBSERVACOES]
    return [{"n": i + 1, "texto": t} for i, t in enumerate(linhas)]


def _renderizar(request, rel, ficha, imprimir=False, em_branco=False):
    linhas = list(ficha.linhas.all())
    valores = [l.valor for l in linhas if l.valor is not None]
    total = ficha.valor_total if ficha.valor_total is not None else (sum(valores, Decimal("0")) if valores else None)
    contexto = {
        "rel": rel, "ficha": ficha, "linhas": linhas, "obs": _linhas_observacoes(ficha),
        "total": total, "imprimir": imprimir, "em_branco": em_branco,
        "bancos": BANCOS, "contato": CONTATO, "favorecido": FAVORECIDO,
        "igreja": IGREJA, "versiculo": VERSICULO,
    }
    return render(request, "ficha_diaria/ficha.html", contexto)


@login_required
def ficha_editar(request, relatorio_pk):
    rel = get_object_or_404(Relatorio.objects.select_related("livraria"), pk=relatorio_pk)
    ficha = _obter_ficha(rel)
    if request.method == "POST":
        with transaction.atomic():
            linhas = list(ficha.linhas.all())
            for l in linhas:
                l.data_abertura = (request.POST.get(f"l{l.pk}_data") or "").strip()[:20]
                l.valor = _decimal(request.POST.get(f"l{l.pk}_valor"))
                for n in range(1, 6):
                    setattr(l, f"testemunha_{n}", (request.POST.get(f"l{l.pk}_t{n}") or "").strip()[:100])
            ficha.linhas.bulk_update(
                linhas, ["data_abertura", "valor"] + [f"testemunha_{n}" for n in range(1, 6)])
            obs = [(request.POST.get(f"obs_{i}") or "").strip() for i in range(1, LINHAS_OBSERVACOES + 1)]
            ficha.observacoes = "\n".join(obs).rstrip("\n")
            ficha.valor_total = _decimal(request.POST.get("valor_total"))
            ficha.save()
        messages.success(request, "Ficha diária salva.")
        return redirect("ficha_editar", relatorio_pk=rel.pk)
    return _renderizar(request, rel, ficha)


@login_required
def ficha_imprimir(request, relatorio_pk):
    """Versão para impressão (1 folha A4). ?em_branco=1 imprime o modelo sem preenchimento."""
    rel = get_object_or_404(Relatorio.objects.select_related("livraria"), pk=relatorio_pk)
    ficha = _obter_ficha(rel)
    return _renderizar(request, rel, ficha, imprimir=True, em_branco=bool(request.GET.get("em_branco")))
