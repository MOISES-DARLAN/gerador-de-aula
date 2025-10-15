from django.urls import path
from . import views

urlpatterns = [
    # A string vazia '' representa a página raiz do nosso app
    path('', views.gerador_view, name='gerador'),
]