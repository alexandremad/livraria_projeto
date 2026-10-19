from django.urls import path

from . import views

urlpatterns = [
    path("", views.RelatorioLista.as_view(), name="relatorio_lista"),
    path("relatorios/novo/", views.relatorio_novo, name="relatorio_novo"),
    path("relatorios/<int:pk>/", views.relatorio_folha, name="relatorio_folha"),
    path("relatorios/<int:pk>/imprimir/", views.relatorio_imprimir, name="relatorio_imprimir"),
    path("relatorios/<int:pk>/excluir/", views.relatorio_excluir, name="relatorio_excluir"),
    path("livrarias/", views.LivrariaLista.as_view(), name="livraria_lista"),
    path("livrarias/nova/", views.LivrariaNova.as_view(), name="livraria_nova"),
    path("livrarias/<int:pk>/editar/", views.LivrariaEditar.as_view(), name="livraria_editar"),
    path("livrarias/<int:pk>/excluir/", views.LivrariaExcluir.as_view(), name="livraria_excluir"),
]

