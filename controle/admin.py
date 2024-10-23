from django.contrib import admin
from .models import Barbeiro, TipoCorte, Produto

@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ['nome']

@admin.register(TipoCorte)
class TipoCorteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'estoque']
