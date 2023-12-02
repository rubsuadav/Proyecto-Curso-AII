# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Whooosh imports
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.index import open_dir, create_in, exists_in
from whoosh.query import Every, And

# Python imports
import shelve

# Local imports
from .population import populateDB
from .forms import RegisterForm, LoginForm
from .models import Pelicula, Director, Generos, Plataforma


def index(request):
    return render(request, 'index.html', {'peliculas': Pelicula.objects.all(), 'directores': Director.objects.all(), 'generos': Generos.objects.all(), 'plataformas': Plataforma.objects.all()})


# AGRUPACIONES #################################################
def peliculas_agrupadas_por_plataforma(request):
    request.session['origen'] = 'plataforma'
    page = request.GET.get('page', 1)
    plataformas = Plataforma.objects.all()
    peliculas_por_director = {plataforma: Pelicula.objects.filter(
        plataforma=plataforma) for plataforma in plataformas}
    paginator = Paginator(list(peliculas_por_director.items()), 4)
    try:
        peliculas_pagina = paginator.page(page)
    except PageNotAnInteger:
        peliculas_pagina = paginator.page(1)
    except EmptyPage:
        peliculas_pagina = paginator.page(paginator.num_pages)

    return render(request, 'peliculas_agrupadas_por_plataforma.html', {'peliculas_plataforma': peliculas_pagina})


def peliculas_agrupadas_por_genero(request):
    request.session['origen'] = 'genero'
    page = request.GET.get('page', 1)
    generos = Generos.objects.all()
    peliculas_por_genero = {}  # Diccionario de generos con sus peliculas
    for genero in generos:
        peliculas = Pelicula.objects.filter(generos=genero)
        peliculas_unicas = {}  # Diccionario de peliculas unicas
        for pelicula in peliculas:
            # Si el título de la película no esta en el diccionario de peliculas unicas
            if pelicula.titulo not in peliculas_unicas:
                # Añadimos la pelicula al diccionario de peliculas unicas
                peliculas_unicas[pelicula.titulo] = pelicula

        # Añadimos al diccionario de peliculas por genero las peliculas unicas
        peliculas_por_genero[genero] = peliculas_unicas.values()
    paginator = Paginator(list(peliculas_por_genero.items()), 4)
    try:
        peliculas_pagina = paginator.page(page)
    except PageNotAnInteger:
        peliculas_pagina = paginator.page(1)
    except EmptyPage:
        peliculas_pagina = paginator.page(paginator.num_pages)

    return render(request, 'peliculas_agrupadas_por_genero.html', {'peliculas_genero': peliculas_pagina})


# BÚSQUEDAS #################################################
def buscar(request):
    pass


# DETALLES #################################################
def detalles_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    return render(request, 'detalles_pelicula.html', {'pelicula': pelicula, 'origen': request.session.get('origen')})


# GESTION DE USUARIOS #################################################
@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if User.objects.filter(username__iexact=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(email__iexact=email).exists():
                form.add_error(
                    'email', 'El email ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(first_name__iexact=form.cleaned_data['first_name']).exists():
                form.add_error(
                    'first_name', 'El nombre ya existe')
                return render(request, 'registro.html', {'form': form})
            user = User.objects.create_user(
                username=username, email=email, password=form.cleaned_data['password'])

            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            return redirect('login')
    return render(request, 'registro.html', {'form': form})


@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data["password"]

            if not User.objects.filter(username=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario no existe')
                return render(request, 'login.html', {'form': form})
            if not check_password(password, User.objects.get(username=username).password):
                form.add_error(
                    'password', 'La contraseña no es correcta')
                return render(request, 'login.html', {'form': form})
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    return render(request, 'login.html', {'form': form})


# Cerrar sesión, sólo los usuarios autenticados pueden cerrar sesión
@user_passes_test(lambda u: u.is_authenticated, login_url='index')
def logout_session(request):
    logout(request)
    return redirect('index')


# CARGAR DATOS #################################################
# Cargar BBDD, sólo los usuarios autenticados pueden cargar la BBDD
@user_passes_test(lambda u: u.is_authenticated, login_url='index')
def cargar(request):
    if request.method == 'POST':
        if request.POST['cargar'] == 'Si':
            populateDB()
            return render(request, 'cargar_BD.html', {'peliculas': Pelicula.objects.all(),
                                                      'directores': Director.objects.all(),
                                                      'generos': Generos.objects.all(),
                                                      'plataformas': Plataforma.objects.all()})
        else:
            return redirect("index")
    return render(request, 'confirmar_carga_BD.html')
