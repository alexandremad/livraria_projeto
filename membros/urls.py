from django.urls import path
from .views import HomeView, MembroCreateView, MembroUpdateView, MembroDeleteView, MembroDetailView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('cadastrar/', MembroCreateView.as_view(), name='cadastrar_membro'),
    path('detalhe/<int:pk>/', MembroDetailView.as_view(), name='detalhe_membro'), # Nova rota
    path('editar/<int:pk>/', MembroUpdateView.as_view(), name='editar_membro'),
    path('apagar/<int:pk>/', MembroDeleteView.as_view(), name='apagar_membro'),
]