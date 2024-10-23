from django.urls import path
from . import views

urlpatterns = [
    path('', views.agendamentos, name='agendamentos'),
    path('remover/<int:agendamento_id>/', views.remover_agendamento, name='remover_agendamento'),
    path('confirmar-pagamento/<int:agendamento_id>/', views.confirmar_pagamento, name='confirmar_pagamento'),
    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('marcar_horario/', views.marcar_horario, name='marcar_horario'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
	path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
	
    
    path('admin-custom/', views.admin_custom, name='admin_custom'),
	 
	 #Produto
    path('adicionar-produto/', views.adicionar_produto, name='adicionar_produto'),
    path('editar-produto/<int:id>/', views.editar_produto, name='editar_produto'),
    path('remover-produto/<int:id>/', views.remover_produto, name='remover_produto'),

    # Serviços (Cortes)
    path('adicionar-servico/', views.adicionar_servico, name='adicionar_servico'),
    path('editar-servico/<int:servico_id>/', views.editar_servico, name='editar_servico'),
    path('remover-servico/<int:servico_id>/', views.remover_servico, name='remover_servico'),
    
    # Barbeiros
    path('adicionar-barbeiro/', views.adicionar_barbeiro, name='adicionar_barbeiro'),
    path('editar-barbeiro/<int:barbeiro_id>/', views.editar_barbeiro, name='editar_barbeiro'),
    path('remover-barbeiro/<int:barbeiro_id>/', views.remover_barbeiro, name='remover_barbeiro'),
]
