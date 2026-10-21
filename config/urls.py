from django.contrib import admin
from django.urls import include, path
from estoque import views  # Importa as views do aplicativo 'estoque'
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static

# ... sua lista urlpatterns como está ...



urlpatterns = [

    
    # Painel Administrativo
    path('admin/', admin.site.urls),
    
    # Página Inicial e Autenticação
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio'),
    path("contas/", include("django.contrib.auth.urls")),
    
    # Apps do Sistema
    path("livraria/", include("estoque.urls")),
    path('ficha/', include('ficha_diaria.urls')),
    path("", include("membros.urls")), 
    path("reuniao/", include("reuniao.urls")),
]

# Essencial para carregar fotos e documentos enviados durante o desenvolvimento
if settings.DEBUG:
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
