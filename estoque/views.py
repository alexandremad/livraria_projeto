from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .constantes import CABECALHO_FIXO, LINHAS_LIVRES
from .forms import CabecalhoRelatorioForm, LivrariaForm, NovoRelatorioForm
from .models import CAMPOS_CABECALHO, PORTES, Livraria, Relatorio, Secao

from django.shortcuts import render

def inicio(request):
    return render(request, 'estoque/inicio.html')

# sigla usada no nome do <input>  ->  campo do model
CAMPOS_QTD = [("ei", "estoque_inicial"), ("en", "entrada"), ("tr", "transferencia"), ("qv", "qtd_vendas")]


def _inteiro(texto):
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        return None


def _decimal(texto):
    texto = (texto or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


# ------------------------------------------------------------------ LIVRARIAS
class LivrariaLista(LoginRequiredMixin, ListView):
    model = Livraria
    template_name = "estoque/livraria_list.html"

    def get_queryset(self):
        return Livraria.objects.select_related("principal")


class LivrariaNova(LoginRequiredMixin, CreateView):
    model = Livraria
    form_class = LivrariaForm
    template_name = "estoque/livraria_form.html"
    success_url = reverse_lazy("livraria_lista")


class LivrariaEditar(LoginRequiredMixin, UpdateView):
    model = Livraria
    form_class = LivrariaForm
    template_name = "estoque/livraria_form.html"
    success_url = reverse_lazy("livraria_lista")


class LivrariaExcluir(LoginRequiredMixin, DeleteView):
    model = Livraria
    template_name = "estoque/confirmar_exclusao.html"
    success_url = reverse_lazy("livraria_lista")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Esta livraria possui relatórios ou livrarias auxiliares. "
                                         "Em vez de excluir, desmarque \"Ativa\".")
            return redirect("livraria_lista")


# ------------------------------------------------------------------ RELATÓRIOS
class RelatorioLista(LoginRequiredMixin, ListView):
    model = Relatorio
    template_name = "estoque/relatorio_list.html"

    def get_queryset(self):
        return Relatorio.objects.select_related("livraria")


@login_required
def relatorio_novo(request):
    form = NovoRelatorioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            rel = Relatorio(livraria=form.cleaned_data["livraria"], referencia=form.cleaned_data["mes"])
            rel.preencher_cabecalho_da_livraria()
            rel.save()
            rel.criar_linhas()
        return redirect("relatorio_folha", pk=rel.pk)
    return render(request, "estoque/relatorio_novo.html", {"form": form})


@login_required
def relatorio_excluir(request, pk):
    rel = get_object_or_404(Relatorio, pk=pk)
    if request.method == "POST":
        rel.delete()
        messages.success(request, "Relatório excluído.")
        return redirect("relatorio_lista")
    return render(request, "estoque/confirmar_exclusao.html", {"object": rel})


def montar_paginas(rel):
    """Monta as 3 páginas / 2 colunas exatamente como o papel."""
    itens_por_secao = {}
    for item in rel.itens.select_related("produto").order_by("produto__ordem"):
        itens_por_secao.setdefault(item.produto.secao_id, []).append(item)

    livres = {}
    for linha in rel.linhas_livres.all():
        livres.setdefault((linha.pagina, linha.coluna), []).append(linha)

    secoes = list(Secao.objects.all())
    paginas = []
    for pag in (1, 2, 3):
        colunas = []
        for col in (1, 2):
            blocos, total_qtd, total_custo = [], 0, Decimal("0")
            for sec in (s for s in secoes if s.pagina == pag and s.coluna == col):
                itens = itens_por_secao.get(sec.id, [])
                blocos.append({"secao": sec, "itens": itens})
                for it in itens:
                    total_qtd += it.qtd_vendas or 0
                    total_custo += it.custo_total or 0
            linhas_livres = livres.get((pag, col), [])
            for it in linhas_livres:
                total_qtd += it.qtd_vendas or 0
                total_custo += it.custo_total or 0
            colunas.append({
                "numero": col,
                "blocos": blocos,
                "livres": linhas_livres,
                "livres_cabecalho": LINHAS_LIVRES.get((pag, col), {}).get("cabecalho", False),
                "total_qtd": total_qtd,
                "total_custo": total_custo,
            })
        paginas.append({"numero": pag, "colunas": colunas})
    return paginas


def _renderizar_folha(request, rel, imprimir=False, em_branco=False):
    contexto = {
        "rel": rel, "paginas": montar_paginas(rel), "fixo": CABECALHO_FIXO, "portes": PORTES,
        "imprimir": imprimir, "em_branco": em_branco,
    }
    return render(request, "estoque/relatorio_folha.html", contexto)


@login_required
def relatorio_folha(request, pk):
    rel = get_object_or_404(Relatorio.objects.select_related("livraria"), pk=pk)
    if request.method == "POST":
        with transaction.atomic():
            form = CabecalhoRelatorioForm(request.POST, instance=rel)
            if form.is_valid():
                form.save()
            itens = list(rel.itens.all())
            for it in itens:
                for sigla, campo in CAMPOS_QTD:
                    setattr(it, campo, _inteiro(request.POST.get(f"i{it.pk}_{sigla}")))
            rel.itens.bulk_update(itens, [c for _, c in CAMPOS_QTD])

            livres = list(rel.linhas_livres.all())
            for ln in livres:
                for sigla, campo in CAMPOS_QTD:
                    setattr(ln, campo, _inteiro(request.POST.get(f"l{ln.pk}_{sigla}")))
                ln.codigo = (request.POST.get(f"l{ln.pk}_cod") or "").strip()[:10]
                ln.nome = (request.POST.get(f"l{ln.pk}_nome") or "").strip()[:120]
                ln.valor_unit = _decimal(request.POST.get(f"l{ln.pk}_val"))
            rel.linhas_livres.bulk_update(
                livres, [c for _, c in CAMPOS_QTD] + ["codigo", "nome", "valor_unit"])
            rel.save()  # atualiza "atualizado_em"
        messages.success(request, "Relatório salvo.")
        return redirect("relatorio_folha", pk=rel.pk)
    return _renderizar_folha(request, rel)


@login_required
def relatorio_imprimir(request, pk):
    """Versão para impressão (3 folhas A4). ?em_branco=1 imprime o modelo sem números."""
    rel = get_object_or_404(Relatorio.objects.select_related("livraria"), pk=pk)
    return _renderizar_folha(request, rel, imprimir=True, em_branco=bool(request.GET.get("em_branco")))
