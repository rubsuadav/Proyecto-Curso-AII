from django import forms
from django.core.exceptions import ValidationError
import re


def validate_email(value):
    if not re.match(r'^\w+([.-]?\w+)*@(gmail|hotmail|outlook)\.com$', value):
        raise ValidationError(
            'el email debe de ser de gmail, hotmail o outlook')


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=100,
        min_length=6,
        widget=forms.TextInput,
        required=True
    )
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=100,
        widget=forms.EmailInput,
        required=True,
        validators=[validate_email]
    )
    password = forms.CharField(
        label='Contraseña',
        max_length=100,
        min_length=6,
        widget=forms.PasswordInput,
        required=True
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=100,
        min_length=3,
        widget=forms.TextInput,
        required=True
    )
    last_name = forms.CharField(
        label='Apellidos',
        max_length=100,
        min_length=3,
        widget=forms.TextInput,
        required=True
    )


class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100,
                               min_length=6, widget=forms.TextInput, required=True)
    password = forms.CharField(label='Contraseña', max_length=100, min_length=6,
                               widget=forms.PasswordInput, required=True)
