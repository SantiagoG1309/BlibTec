from django import forms
from .models import Libro, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'titulo',
            'autor',
            'editorial',
            'año_publicacion',
            'descripcion',
            'cantidad_total',
            'categoria'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'cantidad_total': 'Cantidad disponible para préstamo',
            'categoria': 'Categoría del libro'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['descripcion']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})