from django.urls import path

from . import views

urlpatterns = [
    path("<int:relatorio_pk>/", views.ficha_editar, name="ficha_editar"),
    path("<int:relatorio_pk>/imprimir/", views.ficha_imprimir, name="ficha_imprimir"),
]
