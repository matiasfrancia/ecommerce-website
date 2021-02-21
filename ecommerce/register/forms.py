from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation

class RegisterForm(UserCreationForm):

    nombre = forms.CharField(max_length = 200)
    apellido = forms.CharField(max_length = 200)
    email = forms.EmailField()

    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput,
        help_text= '''
        Tu contraseña no puede ser muy similar al resto de tus datos,
         debe contener al menos 8 caracteres, 
         no puede ser muy comúm ni sólo contener números.''',
    )

    password2 = forms.CharField(
        label="Repetir contraseña",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta():
        model = User
        fields = ["nombre", "apellido", "email", "username", "password1", "password2"]
        help_texts = {
            "username": "Máximo 150 caracteres. Letras, números y @/./+/-/_.",
        }
        labels = {
            "username": "Nombre de usuario",
        }
        errors = {
            
        }