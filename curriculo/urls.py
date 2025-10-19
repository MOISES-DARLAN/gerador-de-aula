from django.urls import path
from . import views

urlpatterns = [
    # URLs Gerador e Autenticação
    path('', views.gerador_view, name='gerador'),
    path('plano/pdf/<int:plano_id>/', views.gerar_pdf_view, name='gerar_pdf'),
    path('plano/<int:plano_id>/', views.plano_detalhe_view, name='plano_detalhe'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.registrar_view, name='registrar'),
    path('perfil/', views.perfil_view, name='perfil'),

    # --- NOVAS URLs CRUD ---
    # Áreas
    path('gerenciar/areas/', views.listar_areas, name='listar_areas'),
    path('gerenciar/areas/nova/', views.criar_area, name='criar_area'),
    path('gerenciar/areas/editar/<int:pk>/', views.editar_area, name='editar_area'),
    path('gerenciar/areas/deletar/<int:pk>/', views.deletar_area, name='deletar_area'),
    # Componentes
    path('gerenciar/componentes/', views.listar_componentes, name='listar_componentes'),
    path('gerenciar/componentes/novo/', views.criar_componente, name='criar_componente'),
    path('gerenciar/componentes/editar/<int:pk>/', views.editar_componente, name='editar_componente'),
    path('gerenciar/componentes/deletar/<int:pk>/', views.deletar_componente, name='deletar_componente'),
]