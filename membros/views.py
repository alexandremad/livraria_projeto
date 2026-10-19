from django.urls import reverse_lazy
from .models import Membro
from .forms import MembroForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView # Importe DetailView
from .models import Membro
from .forms import MembroForm

# 1. Página inicial (Listar membros)
class HomeView(ListView):
    model = Membro
    template_name = 'membros/home.html'
    context_object_name = 'membros'

# 2. Cadastrar membro
class MembroCreateView(CreateView):
    model = Membro
    form_class = MembroForm
    template_name = 'membros/form_membro.html'
    success_url = reverse_lazy('home')

# 3. Editar membro
class MembroUpdateView(UpdateView):
    model = Membro
    form_class = MembroForm
    template_name = 'membros/form_membro.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Se chegou aqui, o formulário é válido e vai salvar
        print(">>> FORMULÁRIO VÁLIDO. A SALVAR...")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Se chegou aqui, o Django REJEITOU os dados. Vamos ver o motivo no terminal!
        print(">>> ERRO DE VALIDAÇÃO DO FORMULÁRIO:")
        print(form.errors)
        return super().form_invalid(form)

# 4. Apagar membro
class MembroDeleteView(DeleteView):
    model = Membro
    template_name = 'membros/confirm_delete.html'
    success_url = reverse_lazy('home')

    # 5. Visualizar Ficha do Membro
class MembroDetailView(DetailView):
    model = Membro
    template_name = 'membros/detalhe_membro.html'
    context_object_name = 'membro'