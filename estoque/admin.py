from django.contrib import admin

from .models import ItemRelatorio, Livraria, LinhaLivre, Produto, Relatorio, Secao


@admin.register(Livraria)
class LivrariaAdmin(admin.ModelAdmin):
    list_display = ("nome", "principal", "cidade", "uf", "ativa")
    list_filter = ("ativa", "uf")
    search_fields = ("nome", "cidade", "cod_totvs")


@admin.register(Secao)
class SecaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "pagina", "coluna", "ordem")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "secao", "valor_unit", "ativo")
    list_filter = ("secao", "ativo")
    list_editable = ("valor_unit", "ativo")
    search_fields = ("codigo", "nome")


class ItemInline(admin.TabularInline):
    model = ItemRelatorio
    extra = 0


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ("livraria", "referencia", "atualizado_em")
    list_filter = ("livraria",)
