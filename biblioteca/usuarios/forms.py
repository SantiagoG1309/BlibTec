from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):
    telefono = forms.CharField(max_length=15, required=False)
    direccion = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'telefono', 'direccion']
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'CLIENTE'  # Asignar rol CLIENTE automáticamente
        if commit:
            user.save()
        return user

class RegistroAdminForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=True)
    direccion = forms.CharField(widget=forms.Textarea, required=True)
    rol = forms.ChoiceField(required=True, initial='ADMINISTRADOR')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_superadmin:
            self.fields['rol'].choices = [
                ('ADMINISTRADOR', 'Administrador'),
                ('SUPERADMINISTRADOR', 'Super Administrador')
            ]
        else:
            self.fields['rol'].choices = [
                ('ADMINISTRADOR', 'Administrador')
            ]

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'telefono', 'direccion', 'rol']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = self.cleaned_data['rol']
        if commit:
            user.save()
        return user

class ActualizarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password'}))