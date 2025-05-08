from django import forms
from .models import Libro

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
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'cantidad_total': 'Cantidad disponible para préstamo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['descripcion']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})