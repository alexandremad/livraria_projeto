from django.contrib import admin
from .models import Membro


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "cidade", "celular")
    search_fields = ("nome", "cpf")