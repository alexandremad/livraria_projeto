from django.contrib import admin

from .models import FichaDiaria, FichaDiariaLinha


class LinhaInline(admin.TabularInline):
    model = FichaDiariaLinha
    extra = 0


@admin.register(FichaDiaria)
class FichaDiariaAdmin(admin.ModelAdmin):
    list_display = ("relatorio", "valor_total", "atualizado_em")
    inlines = [LinhaInline]
