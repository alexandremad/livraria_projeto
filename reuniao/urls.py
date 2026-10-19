from django.urls import path

from . import views

urlpatterns = [
    path("", views.CadastroView.as_view(), name="reuniao_cadastro"),
    path("impressao/", views.ImpressaoView.as_view(), name="reuniao_impressao"),
]
