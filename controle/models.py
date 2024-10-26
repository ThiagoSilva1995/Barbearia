from django.db import models
from django.db.models import Sum

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

class Barbeiro(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15, default='000000000')

    def __str__(self):
        return self.nome

class TipoCorte(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)  # Estoque dos produtos

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"




class Agendamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE)
    tipo_corte = models.ManyToManyField(TipoCorte)  # Alterado para ManyToManyField
    data = models.DateField()
    hora = models.TimeField()
    pago = models.BooleanField(default=False)
    produtos = models.ManyToManyField(Produto, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.barbeiro} - {self.data} {self.hora}"

    def calcular_valor_total(self):
        return self.tipo_corte.aggregate(total=Sum('preco'))['total'] or 0  # Soma os preços
