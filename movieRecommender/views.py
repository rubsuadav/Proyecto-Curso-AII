# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Whooosh imports
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.index import open_dir, create_in, exists_in
from whoosh.query import Every, And

# Python imports
import shelve

# Local imports
from .population import populateDB
from .forms import RegisterForm, LoginForm
from .recommendations import transformPrefs, calculateSimilarItems
from .models import Pelicula, Director, Generos, Plataforma


def index(request):
    return render(request, 'index.html', {'peliculas': Pelicula.objects.all(), 'directores': Director.objects.all(), 'generos': Generos.objects.all(), 'plataformas': Plataforma.objects.all()})


@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(email=email).exists():
                form.add_error(
                    'email', 'El email ya existe')
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

            if not User.objects.filter(username=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario no existe')
                return render(request, 'login.html', {'form': form})
            user = authenticate(username=username,
                                password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect('index')
    return render(request, 'login.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated, login_url='index')
def logout_session(request):
    logout(request)
    return redirect('index')


## FUNCIÓN AUXILIAR PARA CARGAR EL SISTEMA DE RECOMENDACIÓN ##############################
"""def loadDict():
    Prefs = {}
    shelf = shelve.open("dataRS.dat")
    ratings = Puntuacion.objects.all()
    for ra in ratings:
        plataformna = int(ra.id_plataforma.id)
        pelicula = int(ra.id_pelicula.id)
        rating = float(ra.puntuacion)
        Prefs.setdefault(plataformna, {})
        Prefs[plataformna][pelicula] = rating
    shelf['Prefs'] = Prefs
    shelf['ItemsPrefs'] = transformPrefs(Prefs)
    shelf['SimItems'] = calculateSimilarItems(Prefs, n=10)
    shelf.close()


# Cargar sistema de Recomendacion (RS), sólo los usuarios autenticados pueden cargar el RS
@user_passes_test(lambda u: u.is_authenticated, login_url='index')
def loadRS(request):
    if request.method == 'POST':
        if 'Aceptar' in request.POST:
            loadDict()
            mensaje = "Se ha cargado el sistema de recomendación correctamente"
            return render(request, 'cargar_SR.html', {'mensaje': mensaje})
        else:
            return redirect("index")
    return render(request, 'confirmar_SR.html')"""


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
