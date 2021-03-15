from django import forms

from .models import Product

class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'category_filter',
            'description',
            'image',
            'price',
            'active',
            ]
        labels = {
            'title': 'Título',
            'category_filter': 'Categoría',
            'description': 'Descripción',
            'image': 'Imagen',
            'price': 'Precio',
            'active': 'Activo',
        }
        help_texts = {
            'category_filter': "Para crear una nueva categoría debes ir a tu cuenta de administrador y presionar el botón 'Categorías'"
        }