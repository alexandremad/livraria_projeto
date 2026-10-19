from django.contrib import admin

from .models import Participante


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ("nome", "setor", "data_cadastro")
    search_fields = ("nome", "setor")
    list_filter = ("setor",)
    date_hierarchy = "data_cadastro"
