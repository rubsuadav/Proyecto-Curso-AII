# Django imports
from django import forms
from django.core.exceptions import ValidationError

# Local imports
from .models import Generos

# Python imports
import re


def validate_email(value):
    if not re.match(r'^\w+([.-]?\w+)*@(gmail|hotmail|outlook)\.com$', value):
        raise ValidationError(
            'el email debe de ser de gmail, hotmail o outlook')


def validate_fecha(value):
    if not re.match(r'^\d{4}$', str(value)):
        raise ValidationError(
            'el año debe de ser de 4 dígitos')


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


class GenerosForm(forms.Form):
    generos = forms.ModelChoiceField(
        queryset=Generos.objects.all(), label='Selecciona el género')


class TituloSinopsisForm(forms.Form):
    busqueda = forms.CharField(label='Introduce las palabras a buscar', max_length=100, min_length=1,
                               widget=forms.TextInput, required=False)


class GeneroTituloForm(forms.Form):
    generos = forms.ModelChoiceField(
        queryset=Generos.objects.all(), label='Selecciona el género')
    busqueda = forms.CharField(label='Introduce las palabras a buscar', max_length=100, min_length=1,
                               widget=forms.TextInput, required=False)


class FechaLanzamientoForm(forms.Form):
    fecha = forms.CharField(label='Introduce el año de lanzamiento', validators=[
        validate_fecha], widget=forms.TextInput, required=True)


class PeliculaBusquedaForm(forms.Form):
    nombre_pelicula = forms.CharField(label='Nombre de la película', max_length=100, min_length=1,
                                      widget=forms.TextInput, required=True)
