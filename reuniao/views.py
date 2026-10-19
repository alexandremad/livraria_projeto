import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from .forms import ParticipanteForm
from .models import Participante


class CadastroView(LoginRequiredMixin, CreateView):
    """Substitui o index.php: nome + região."""
    model = Participante
    form_class = ParticipanteForm
    template_name = "reuniao/cadastro.html"
    success_url = reverse_lazy("reuniao_cadastro")

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, f"{self.object.nome} salvo(a) com sucesso!")
        return resposta


class ImpressaoView(LoginRequiredMixin, ListView):
    """Substitui o impressao.php: lista de presença de uma data (?data_reuniao=AAAA-MM-DD), em 4 colunas."""
    template_name = "reuniao/impressao.html"
    context_object_name = "participantes"

    def get_queryset(self):
        try:
            self.data = datetime.date.fromisoformat(self.request.GET.get("data_reuniao", ""))
        except ValueError:
            self.data = timezone.localdate()
        # mesma ordem do PHP: do cadastro mais recente para o mais antigo
        return Participante.objects.filter(data_cadastro__date=self.data).order_by("-data_cadastro")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["data"] = self.data
        contexto["total_dia"] = len(contexto["participantes"])
        return contexto
