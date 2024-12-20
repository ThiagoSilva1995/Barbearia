from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models.functions import ExtractDay, ExtractMonth


from datetime import datetime, timedelta

from .forms import ClienteForm, ProdutoForm, TipoCorteForm, BarbeiroForm
from .models import Agendamento, Barbeiro, Cliente, TipoCorte, Produto





class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'



def marcar_horario(request):
    if request.method == "POST":
        cliente_id = request.POST.get('cliente')
        barbeiro_id = request.POST.get('barbeiro')
        tipo_corte_ids = request.POST.getlist('tipo_corte')  # Obtendo uma lista de IDs de tipos de corte
        data = request.POST.get('data')
        hora = request.POST.get('hora')



        if Agendamento.objects.filter(barbeiro_id=barbeiro_id, data=data, hora=hora).exists():
            messages.error(request, 'Horário já agendado para o barbeiro.', extra_tags='danger')
            return redirect('marcar_horario')

        if not tipo_corte_ids:
            messages.error(request, 'Nenhum tipo de corte selecionado.', extra_tags='danger')
            return redirect('marcar_horario')

        # Criação do agendamento
        agendamento = Agendamento(cliente_id=cliente_id, barbeiro_id=barbeiro_id, data=data, hora=hora)
        agendamento.save()  # Salva o agendamento antes de adicionar os tipos de corte

        # Adiciona os tipos de corte ao agendamento
        for tipo_corte_id in tipo_corte_ids:
            tipo_corte = TipoCorte.objects.get(id=tipo_corte_id)
            agendamento.tipo_corte.add(tipo_corte)  # Adiciona o tipo de corte ao agendamento

        messages.success(request, 'Horário agendado com sucesso!')
        return redirect('marcar_horario')
    else:
        # Gera a lista de horários disponíveis
        horarios_disponiveis = []
        inicio = datetime.strptime("08:00", "%H:%M")
        fim = datetime.strptime("19:00", "%H:%M")

        while inicio <= fim:
            horarios_disponiveis.append(inicio.strftime("%H:%M"))
            inicio += timedelta(minutes=30)

        clientes = Cliente.objects.all().order_by('nome')
        barbeiros = Barbeiro.objects.all().order_by('nome')
        tipos_corte = TipoCorte.objects.all().order_by('nome')

    return render(request, 'marcar_horario.html', {
        'horarios_disponiveis': horarios_disponiveis,
        'clientes': clientes,
        'barbeiros': barbeiros,
        'tipos_corte': tipos_corte,  # Passa os tipos de corte para o template
    })


def cadastrar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.nome = cliente.nome.title()
            cliente.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cadastrar_cliente')
        else:
            messages.error(request, 'Erro ao cadastrar o cliente. Verifique os dados e tente novamente.')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cadastrar_cliente.html', {'form': form})

def agendamentos(request):
    barbeiro_filter = request.GET.get('barbeiro')
    data_filter = request.GET.get('data')

    # Filtrar apenas os agendamentos que não foram pagos ou confirmados
    agendamentos = Agendamento.objects.filter(is_confirmed=False)

    if barbeiro_filter:
        agendamentos = agendamentos.filter(barbeiro__id=barbeiro_filter)

    if data_filter:
        agendamentos = agendamentos.filter(data=data_filter)

    # Ordenar por data e hora
    agendamentos = agendamentos.order_by('data', 'hora')

    # Define um mapeamento de cores para os barbeiros
    barbeiros_cores = {}
    barbeiros = Barbeiro.objects.all()
    for i, barbeiro in enumerate(barbeiros):
        barbeiros_cores[barbeiro.id] = 'green' if i % 2 == 0 else 'red'

    # Adicionar a cor para cada agendamento
    for agendamento in agendamentos:
        agendamento.cor_barbeiro = barbeiros_cores.get(agendamento.barbeiro.id, 'gray')

    # Paginação
    paginator = Paginator(agendamentos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'agendamentos/agendamentos.html', {
        'page_obj': page_obj,
        'barbeiros': barbeiros,
        'agendamentos': [{
            'id': agendamento.id,
            'cliente': agendamento.cliente.nome,
            'barbeiro': agendamento.barbeiro.nome,
            'cor_barbeiro': agendamento.cor_barbeiro,  # Cor adicionada ao contexto
            'tipos_corte': [str(corte) for corte in agendamento.tipo_corte.all()],
            'data': agendamento.data,
            'hora': agendamento.hora,
        } for agendamento in page_obj]
    })

def remover_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.delete()
    messages.success(request, "Agendamento removido com sucesso!")
    return redirect('agendamentos')  # Redirecione para a lista de agendamentos

def confirmar_pagamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    produtos = Produto.objects.all()
    tipos_corte = TipoCorte.objects.all()  
    
    # Calcular o valor total dos cortes selecionados
    valor_total = sum(corte.preco for corte in agendamento.tipo_corte.all())

    if request.method == 'POST':
        total_pago = valor_total
        produtos_selecionados = request.POST.getlist('produtos')
        quantidades = request.POST.getlist('quantidades')

        # Iterar sobre produtos e quantidades
        for i, produto_id in enumerate(produtos_selecionados):
            produto = get_object_or_404(Produto, id=produto_id)
            quantidade = int(quantidades[i])

            if produto.estoque >= quantidade:
                produto.estoque -= quantidade
                produto.save()
                agendamento.produtos.add(produto)
                total_pago += produto.preco * quantidade
            else:
                messages.error(request, f"O produto {produto.nome} não tem estoque suficiente.")
                return redirect('agendamentos/confirmar_pagamento', agendamento_id=agendamento_id)

        # Atualiza o agendamento e define como pago e confirmado
        agendamento.pago = True
        agendamento.is_confirmed = True 
        agendamento.save()

        # Adiciona a mensagem de confirmação e limpa a fila antes do redirecionamento
        messages.success(request, 'Pagamento confirmado com sucesso!')
        list(messages.get_messages(request))  
        return redirect('agendamentos')  

    # Renderiza a página de confirmação de pagamento com tipos de corte incluídos
    return render(request, 'agendamentos/confirmar_pagamento_cliente.html', {
        'agendamento': agendamento,
        'produtos': produtos,
        'tipos_corte': tipos_corte,  
        'valor_total': valor_total
    })

def estatisticas(request):
    # Total de Clientes Atendidos
    total_clientes_atendidos = Agendamento.objects.filter(pago=True).values('cliente').distinct().count()

    # Receita Total (cortes + produtos)
    receita_cortes = Agendamento.objects.filter(pago=True).aggregate(Sum('tipo_corte__preco'))['tipo_corte__preco__sum'] or 0
    receita_produtos = Agendamento.objects.filter(pago=True).aggregate(Sum('produtos__preco'))['produtos__preco__sum'] or 0
    receita_total = receita_cortes + receita_produtos

    # Número de Agendamentos por Barbeiro - Ordenado pelo nome do barbeiro
    agendamentos_por_barbeiro = Barbeiro.objects.annotate(total_agendamentos=Count('agendamento')).order_by('nome')

    # Cortes Mais Populares - Ordenado pelo nome do corte
    cortes_populares = Agendamento.objects.values('tipo_corte__nome').annotate(total=Count('tipo_corte')).order_by('tipo_corte__nome')

    # Clientes Fiéis - Organizando em ordem alfabética
    clientes_fieis = Cliente.objects.annotate(total_visitas=Count('agendamento')).order_by('nome')

    # Total de Produtos Vendidos
    total_produtos_vendidos = Produto.objects.filter(agendamento__in=Agendamento.objects.filter(pago=True)).count()

    # Produtos vendidos e suas quantidades - Ordenado pelo nome do produto
    produtos_vendidos = Agendamento.objects.filter(pago=True).values('produtos__nome').annotate(total_vendido=Count('produtos')).order_by('produtos__nome')

    # Lista de todos os produtos com suas quantidades em estoque - Ordenado pelo nome do produto
    produtos = Produto.objects.all().order_by('nome')

    # Aniversariantes do Mês a partir de hoje - Ordenado pela data de nascimento (dia e mês)
    hoje = timezone.now()
    dia_atual = hoje.day
    mes_atual = hoje.month
    aniversariantes_do_mes = Cliente.objects.filter(
        Q(data_nascimento__month=mes_atual) & 
        Q(data_nascimento__day__gte=dia_atual-1)
    ).annotate(
        dia_nascimento=ExtractDay('data_nascimento'),
        mes_nascimento=ExtractMonth('data_nascimento')
    ).order_by('mes_nascimento', 'dia_nascimento')

    context = {
        'total_clientes_atendidos': total_clientes_atendidos,
        'receita_total': receita_total,
        'agendamentos_por_barbeiro': agendamentos_por_barbeiro,
        'cortes_populares': cortes_populares,
        'clientes_fieis': clientes_fieis,
        'total_produtos_vendidos': total_produtos_vendidos,
        'produtos_vendidos': produtos_vendidos,
        'produtos': produtos,
        'aniversariantes_do_mes': aniversariantes_do_mes,
    }

    return render(request, 'estatisticas.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_custom(request):
    # Consultar os produtos, barbeiros e tipos de corte
    produtos = Produto.objects.all()
    barbeiros = Barbeiro.objects.all()
    tipos_corte = TipoCorte.objects.all()

    # Obter a data atual
    hoje = timezone.now()

    # Calcular o domingo e o sábado da semana atual
    domingo_atual = hoje - timedelta(days=hoje.weekday() + 1)  # Último domingo
    sabado_atual = domingo_atual + timedelta(days=6)  # Próximo sábado

    # Calcular o valor total e o valor semanal dos cortes para cada barbeiro
    for barbeiro in barbeiros:
        # Filtrar os agendamentos feitos por este barbeiro com pagamento confirmado
        barbeiro_agendamentos = Agendamento.objects.filter(
            barbeiro=barbeiro,
            is_confirmed=True
        )
        
        # Somar o valor de cada corte realizado pelo barbeiro
        barbeiro.valor_total = sum(
            sum(corte.preco for corte in agendamento.tipo_corte.all())
            for agendamento in barbeiro_agendamentos
        )

        # Calcular o valor semanal
        barbeiro.valor_semanal = sum(
            sum(corte.preco for corte in agendamento.tipo_corte.all())
            for agendamento in barbeiro_agendamentos.filter(
                data__gte=domingo_atual,
                data__lte=sabado_atual
            )
        )

    # Calcular o valor total acumulado de todos os barbeiros
    valor_total_geral = sum(barbeiro.valor_total for barbeiro in barbeiros)

    context = {
        'produtos': produtos,
        'barbeiros': barbeiros,
        'tipos_corte': tipos_corte,
        'valor_total_geral': valor_total_geral  # Passa o valor total geral para o template
    }

    return render(request, 'administrador/admin_custom.html', context)




#Produto
@user_passes_test(lambda u: u.is_superuser)
def adicionar_produto(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = ProdutoForm()
    return render(request, 'administrador/produto/adicionar_produto.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'administrador/produto/editar_produto.html', {'form': form, 'produto': produto})


@user_passes_test(lambda u: u.is_superuser)
def remover_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    return redirect('admin_custom')



# Serviços
@user_passes_test(lambda u: u.is_superuser)
def adicionar_servico(request):
    if request.method == "POST":
        form = TipoCorteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = TipoCorteForm()
    return render(request, 'administrador/servico/adicionar_servico.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def editar_servico(request, servico_id):
    servico = get_object_or_404(TipoCorte, id=servico_id)
    if request.method == 'POST':
        form = TipoCorteForm(request.POST, instance=servico)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = TipoCorteForm(instance=servico)

    return render(request, 'administrador/servico/editar_servico.html', {'form': form, 'servico': servico})


@user_passes_test(lambda u: u.is_superuser)
def remover_servico(request, servico_id):
    servico = get_object_or_404(TipoCorte, id=servico_id)
    servico.delete()
    return redirect('admin_custom')




# Barbeiros
@user_passes_test(lambda u: u.is_superuser)
def adicionar_barbeiro(request):
    if request.method == "POST":
        form = BarbeiroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = BarbeiroForm()

    return render(request, 'administrador/barbeiro/adicionar_barbeiro.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def editar_barbeiro(request, barbeiro_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
    if request.method == 'POST':
        form = BarbeiroForm(request.POST, instance=barbeiro)
        if form.is_valid():
            form.save()
            return redirect('admin_custom')
    else:
        form = BarbeiroForm(instance=barbeiro)

    return render(request, 'administrador/barbeiro/editar_barbeiro.html', {'form': form, 'barbeiro': barbeiro})


@user_passes_test(lambda u: u.is_superuser)
def remover_barbeiro(request, barbeiro_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
    barbeiro.delete()
    return redirect('admin_custom')


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('estatisticas')  # Redirecionar para a tela de estatísticas
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/editar_cliente.html', {'form': form, 'cliente': cliente})


def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente excluído com sucesso!")
        return redirect('estatisticas') 