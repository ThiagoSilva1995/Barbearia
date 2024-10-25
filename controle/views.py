from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView


from datetime import datetime, timedelta

from .forms import ClienteForm, ProdutoForm, TipoCorteForm, BarbeiroForm
from .models import Agendamento, Barbeiro, Cliente, TipoCorte, Produto



def admin_custom(request):
    return render(request, 'administrador/admin_custom.html')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

def marcar_horario(request):
    if request.method == "POST":
        cliente_id = request.POST.get('cliente')
        barbeiro_id = request.POST.get('barbeiro')
        tipo_corte_id = request.POST.get('tipo_corte')
        data = request.POST.get('data')
        hora = request.POST.get('hora')

        if Agendamento.objects.filter(barbeiro_id=barbeiro_id, data=data, hora=hora).exists():
            messages.error(request, 'Horário já agendado para o barbeiro.', extra_tags='danger')
            return redirect('marcar_horario')


        # Cria o agendamento
        agendamento = Agendamento(cliente_id=cliente_id, barbeiro_id=barbeiro_id, tipo_corte_id=tipo_corte_id, data=data, hora=hora)
        agendamento.save()
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

        clientes = Cliente.objects.all()
        barbeiros = Barbeiro.objects.all()
        tipos_corte = TipoCorte.objects.all()  # Obtém todos os tipos de corte

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
    return render(request, 'cadastrar_cliente.html', {'form': form})


def marcar_horario(request):
    if request.method == "POST":
        cliente_id = request.POST.get('cliente')
        barbeiro_id = request.POST.get('barbeiro')
        tipo_corte_id = request.POST.get('tipo_corte')
        data = request.POST.get('data')
        hora = request.POST.get('hora')

        # Verifica se o horário já está agendado
        if Agendamento.objects.filter(barbeiro_id=barbeiro_id, data=data, hora=hora).exists():
            messages.error(request, 'Horário já agendado para o barbeiro.')
            return redirect('marcar_horario')

        # Cria o agendamento
        agendamento = Agendamento(cliente_id=cliente_id, barbeiro_id=barbeiro_id, tipo_corte_id=tipo_corte_id, data=data, hora=hora)
        agendamento.save()
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

        clientes = Cliente.objects.all()
        barbeiros = Barbeiro.objects.all()
        tipos_corte = TipoCorte.objects.all()  # Obtém todos os tipos de corte

    return render(request, 'marcar_horario.html', {
        'horarios_disponiveis': horarios_disponiveis,
        'clientes': clientes,
        'barbeiros': barbeiros,
        'tipos_corte': tipos_corte,  # Passa os tipos de corte para o template
    })



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

    # Paginação
    paginator = Paginator(agendamentos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obter todos os barbeiros e produtos
    barbeiros = Barbeiro.objects.all()
    produtos = Produto.objects.all()  # Adicionando a lista de produtos

    return render(request, 'agendamentos.html', {
        'page_obj': page_obj,
        'barbeiros': barbeiros,
        'produtos': produtos,  # Inclua os produtos no contexto
    })



def remover_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.delete()
    messages.success(request, "Agendamento removido com sucesso!")
    return redirect('agendamentos')  # Redirecione para a lista de agendamentos




def confirmar_pagamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    produtos = Produto.objects.all()

    if request.method == 'POST':
        total_pago = agendamento.tipo_corte.preco
        produtos_selecionados = request.POST.getlist('produtos')  # Produtos selecionados
        quantidades = request.POST.getlist('quantidades')  # Quantidades correspondentes

        # Iterar sobre produtos e suas respectivas quantidades
        for i, produto_id in enumerate(produtos_selecionados):
            produto = get_object_or_404(Produto, id=produto_id)
            quantidade = int(quantidades[i])  # Obter a quantidade informada pelo usuário

            # Verificar estoque e ajustar o total pago
            if produto.estoque >= quantidade:
                produto.estoque -= quantidade
                produto.save()
                agendamento.produtos.add(produto)
                total_pago += produto.preco * quantidade
            else:
                messages.error(request, f"O produto {produto.nome} não tem estoque suficiente.")
                return redirect('confirmar_pagamento', agendamento_id=agendamento_id)

        # Marca o agendamento como pago e confirmado
        agendamento.pago = True
        agendamento.is_confirmed = True
        agendamento.save()

        # Redireciona de volta para os agendamentos
        messages.success(request, "Pagamento confirmado e estoque atualizado!")
        return redirect('agendamentos')

    return render(request, 'confirmar_pagamento_cliente.html', {
        'agendamento': agendamento,
        'produtos': produtos
    })






def estatisticas(request):
    # Total de Clientes Atendidos
    total_clientes_atendidos = Agendamento.objects.filter(pago=True).values('cliente').distinct().count()

    # Receita Total (cortes + produtos)
    receita_cortes = Agendamento.objects.filter(pago=True).aggregate(Sum('tipo_corte__preco'))['tipo_corte__preco__sum'] or 0
    receita_produtos = Agendamento.objects.filter(pago=True).aggregate(Sum('produtos__preco'))['produtos__preco__sum'] or 0
    receita_total = receita_cortes + receita_produtos

    # Número de Agendamentos por Barbeiro
    agendamentos_por_barbeiro = Barbeiro.objects.annotate(total_agendamentos=Count('agendamento'))

    # Cortes Mais Populares
    cortes_populares = Agendamento.objects.values('tipo_corte__nome').annotate(total=Count('tipo_corte')).order_by('-total')

    # Clientes Fiéis - Removendo a limitação para mostrar todos
    clientes_fieis = Cliente.objects.annotate(total_visitas=Count('agendamento')).order_by('nome')  # Organizando em ordem alfabética

    # Total de Produtos Vendidos
    total_produtos_vendidos = Produto.objects.filter(agendamento__in=Agendamento.objects.filter(pago=True)).count()

    # Produtos vendidos e suas quantidades
    produtos_vendidos = Agendamento.objects.filter(pago=True).values('produtos__nome').annotate(total_vendido=Count('produtos')).order_by('-total_vendido')

    # Lista de todos os produtos com suas quantidades em estoque
    produtos = Produto.objects.all()  # Buscando todos os produtos

    # Aniversariantes do Mês
    hoje = timezone.now()
    aniversariantes_do_mes = Cliente.objects.filter(data_nascimento__month=hoje.month).order_by('data_nascimento')

    context = {
        'total_clientes_atendidos': total_clientes_atendidos,
        'receita_total': receita_total,
        'agendamentos_por_barbeiro': agendamentos_por_barbeiro,
        'cortes_populares': cortes_populares,
        'clientes_fieis': clientes_fieis,
        'total_produtos_vendidos': total_produtos_vendidos,
        'produtos_vendidos': produtos_vendidos,
        'produtos': produtos,  # Adicionando a lista de produtos
        'aniversariantes_do_mes': aniversariantes_do_mes,
    }

    return render(request, 'estatisticas.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_custom(request):
    # Consultar os produtos, barbeiros e tipos de corte
    produtos = Produto.objects.all()
    barbeiros = Barbeiro.objects.all()
    tipos_corte = TipoCorte.objects.all()

    # Calcular o valor total dos cortes para cada barbeiro
    for barbeiro in barbeiros:
        # Filtrar os agendamentos feitos por este barbeiro
        barbeiro_agendamentos = Agendamento.objects.filter(barbeiro=barbeiro)
        # Somar o valor de cada corte realizado pelo barbeiro
        barbeiro.valor_total = sum(agendamento.tipo_corte.preco for agendamento in barbeiro_agendamentos)

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
