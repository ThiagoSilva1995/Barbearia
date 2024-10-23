from django import forms
from .models import Cliente, Produto, TipoCorte, Barbeiro

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'data_nascimento']
        widgets = {
            'data_nascimento': forms.SelectDateWidget(years=range(1900, 2025)),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'estoque']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['preco'].widget.attrs.update({'class': 'form-control'})
        self.fields['estoque'].widget.attrs.update({'class': 'form-control'})


class TipoCorteForm(forms.ModelForm):
    class Meta:
        model = TipoCorte
        fields = ['nome', 'preco']


class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = ['nome', 'telefone']

    def __init__(self, *args, **kwargs):
        super(BarbeiroForm, self).__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})