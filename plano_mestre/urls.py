from django.contrib import admin
from django.urls import path, include # Certifique-se de que 'include' está aqui

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('curriculo.urls')), # Adicione esta linha
]