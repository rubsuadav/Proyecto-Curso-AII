# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Whooosh imports
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.query import And, Or
from whoosh.index import open_dir

# Local imports
from .population import populateDB
from .forms import *
from .models import Pelicula, Director, Generos, Plataforma, Pais

# Recomendations imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd


def index(request):
    return render(request, 'index.html', {'peliculas': Pelicula.objects.all(),
                                          'directores': Director.objects.all(), 'generos': Generos.objects.all(), 'plataformas': Plataforma.objects.all(), 'paises': Pais.objects.all()})


# Devuelve las 20 peliculas más populares (con mayor calificación)
def peliculas_mas_populares(request):
    request.session['origen'] = 'populares'
    page = request.GET.get('page', 1)
    peliculas = Pelicula.objects.all().order_by('-calificacion')
    veinte_peliculas = borrar_peliculas_duplicadas_2(peliculas)[:20]
    paginator = Paginator(veinte_peliculas, 4)
    try:
        peliculas_pagina = paginator.page(page)
    except PageNotAnInteger:
        peliculas_pagina = paginator.page(1)
    except EmptyPage:
        peliculas_pagina = paginator.page(paginator.num_pages)

    for pelicula in peliculas_pagina:
        calificacion = pelicula.calificacion
        if calificacion >= 1000000:
            pelicula.calificacion = f'{int(calificacion/1000000)}M'
        elif calificacion >= 1000:
            pelicula.calificacion = f'{int(calificacion/1000)}k'
        elif calificacion == 0:
            pelicula.calificacion = 'Sin calificar'
    return render(request, 'peliculas_mas_populares.html', {'peliculas': peliculas_pagina,
                                                            'totales': veinte_peliculas})


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
def buscar_por_genero(request):
    request.session['origen'] = 'busqueda_genero'
    ix = open_dir("indice_peliculas")
    form = GenerosForm()
    if request.method == 'POST':
        form = GenerosForm(request.POST)
        if form.is_valid():
            generos_input = form.cleaned_data['generos'].nombre
            with ix.searcher() as searcher:
                query = QueryParser("generos", ix.schema).parse(
                    f'"{generos_input}"')
                results = searcher.search(query, limit=None)
                peliculas = borrar_peliculas_duplicadas(results)
                return render(request, 'buscar_peliculas_genero.html', {'peliculas': peliculas, 'form': form})
    else:
        return render(request, 'buscar_peliculas_genero.html', {'form': form})


# Busca por frase en el título o por palabra que esté en la sinopsis
def buscar_titulo_o_sinopsis(request):
    request.session['origen'] = 'busqueda_titulo_o_sinopsis'
    ix = open_dir("indice_peliculas")
    form = TituloSinopsisForm()
    if request.method == 'POST':
        form = TituloSinopsisForm(request.POST)
        if form.is_valid():
            en = form.cleaned_data['busqueda']
            with ix.searcher() as searcher:
                query = MultifieldParser(
                    ["titulo", "sinopsis"], ix.schema, group=OrGroup).parse('"' + en + '"')
                results = searcher.search(query, limit=10)
                peliculas = borrar_peliculas_duplicadas(results)
                return render(request, 'buscar_peliculas_titulo_o_sinopsis.html', {'peliculas': peliculas, 'form': form})
    else:
        return render(request, 'buscar_peliculas_titulo_o_sinopsis.html', {'form': form})


# Busca por genero y por frase/palabra en el título
def buscar_genero_y_titulo(request):
    request.session['origen'] = 'busqueda_genero_y_titulo'
    ix = open_dir("indice_peliculas")
    form = GeneroTituloForm()
    if request.method == 'POST':
        form = GeneroTituloForm(request.POST)
        if form.is_valid():
            en = form.cleaned_data['busqueda']
            sp = form.cleaned_data['generos'].nombre
            with ix.searcher() as searcher:
                titulo_query = QueryParser("titulo", ix.schema).parse(en)
                generos_query = QueryParser(
                    "generos", ix.schema).parse(f'"{sp}"')
                query = And([titulo_query, generos_query])
                results = searcher.search(query, limit=20)
                peliculas = borrar_peliculas_duplicadas(results)
                return render(request, 'buscar_peliculas_generos_y_titulo.html', {'peliculas': peliculas, 'form': form})
    else:
        return render(request, 'buscar_peliculas_generos_y_titulo.html', {'form': form})


# Busca por (genero y por país de producción) o por (país de producción y palabra en la sinopsis)
def buscar_genero_y_pais_o_pais_y_sinopsis(request):
    request.session['origen'] = 'busqueda_genero_y_pais_o_pais_y_sinopsis'
    ix = open_dir("indice_peliculas")
    form = GeneroPaisSinopsisForm()
    if request.method == 'POST':
        form = GeneroPaisSinopsisForm(request.POST)
        if form.is_valid():
            en = form.cleaned_data['busqueda']
            sp = form.cleaned_data['pais'].nombre
            sp2 = form.cleaned_data['generos']
            genero = sp2.nombre if sp2 else None
            with ix.searcher() as searcher:
                pais_query = QueryParser("paises", ix.schema).parse(f'"{sp}"')
                genero_query = QueryParser(
                    "generos", ix.schema).parse(f'"{genero}"')
                sinopsis_query = QueryParser(
                    "sinopsis", ix.schema).parse(en)
                query = Or([And([pais_query, genero_query]), And(
                    [pais_query, sinopsis_query])])  # (pais & genero) || (pais & sinopsis) --> pais & (genero || sinopsis)
                results = searcher.search(query, limit=20)
                peliculas = borrar_peliculas_duplicadas(results)
                return render(request, 'buscar_peliculas_generos_y_pais_o_pais_y_sinopsis.html', {'peliculas': peliculas, 'form': form})
    else:
        return render(request, 'buscar_peliculas_generos_y_pais_o_pais_y_sinopsis.html', {'form': form})


# Busca por fecha de lanzamiento y obtiene las 5 peliculas más recientes y con menor duración
def buscar_fecha_lanzamiento(request):
    request.session['origen'] = 'busqueda_fecha_lanzamiento'
    ix = open_dir("indice_peliculas")
    form = FechaLanzamientoForm()
    if request.method == 'POST':
        form = FechaLanzamientoForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            with ix.searcher() as searcher:
                query = QueryParser("fecha_lanzamiento",
                                    ix.schema).parse(f'"{fecha}"')
                results = searcher.search(
                    query, limit=5, sortedby="duracion", reverse=False)
                peliculas = borrar_peliculas_duplicadas(results)
                return render(request, 'buscar_peliculas_fecha_lanzamiento.html', {'peliculas': peliculas, 'form': form})
        else:
            return render(request, 'buscar_peliculas_fecha_lanzamiento.html', {'form': form})
    else:
        return render(request, 'buscar_peliculas_fecha_lanzamiento.html', {'form': form})


# MÉTODOS AUXILIARES #################################################
def borrar_peliculas_duplicadas(results):
    peliculas_set = set()
    peliculas = []
    for result in results:
        if result['titulo'] not in peliculas_set:
            # Añadimos la pelicula al conjunto de peliculas
            peliculas_set.add(result['titulo'])
            # Añadimos la pelicula a la lista de peliculas
            peliculas.append(result)
    return peliculas


def borrar_peliculas_duplicadas_2(results):
    peliculas_set = set()
    peliculas = []
    for result in results:
        if result.titulo not in peliculas_set:
            # Añadimos la pelicula al conjunto de peliculas
            peliculas_set.add(result.titulo)
            # Añadimos la pelicula a la lista de peliculas
            peliculas.append(result)
    return peliculas


# DETALLES #################################################
def detalles_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    calificacion = pelicula.calificacion
    if calificacion >= 1000000:
        return render(request, 'detalles_pelicula.html', {'pelicula': pelicula,
                                                          'origen': request.session.get('origen'),
                                                          'calificacion': f'{int(calificacion/1000000)}M'})
    elif calificacion >= 1000:
        return render(request, 'detalles_pelicula.html', {'pelicula': pelicula,
                                                          'origen': request.session.get('origen'),
                                                          'calificacion': f'{int(calificacion/1000)}k'})
    elif calificacion == 0:
        return render(request, 'detalles_pelicula.html', {'pelicula': pelicula, 'origen': request.session.get('origen'),
                                                          'calificacion': 'Sin calificar'})


def detalles_plataforma(request, plataforma_id):
    plataforma = get_object_or_404(Plataforma, pk=plataforma_id)
    return render(request, 'detalles_plataforma.html', {'plataforma': plataforma})


# GESTION DE USUARIOS #################################################
@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['first_name']

            if User.objects.filter(username__iexact=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(email__iexact=email).exists():
                form.add_error(
                    'email', 'El email ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(first_name__iexact=firstname).exists():
                form.add_error(
                    'first_name', 'El nombre ya existe')
                return render(request, 'registro.html', {'form': form})
            user = User.objects.create_user(
                username=username, email=email, password=form.cleaned_data['password'])

            user.first_name = firstname
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
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
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


## SISTEMA DE RECOMENDACIÓN BASADO EN CONTENIDOS #################################################

# RECOMENDAR PELÍCULA SEGÚN TÍTULO, Sólo los usuarios autenticados pueden recomendar peliculas
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def recomendar_pelicula(request):
    request.session['origen'] = 'recomendacion1'
    if request.method == 'POST':
        form = PeliculaBusquedaForm(request.POST)
        if form.is_valid():
            nombre_pelicula = form.cleaned_data['nombre_pelicula']
            peliculas_recomendadas = obtener_recomendaciones(nombre_pelicula)
            return render(request, 'peliculas_recomendadas.html', {'peliculas': peliculas_recomendadas, 'form': form})
    else:
        form = PeliculaBusquedaForm()
    return render(request, 'peliculas_recomendadas.html', {'form': form})


# MÉTODOS QUE OBTIENEN LAS RECOMENDACIONES ##########################################
# Método que obtiene las recomendaciones de peliculas
def obtener_recomendaciones(titulo):
    similitud_cos, indices, peliculas = calcular_similitud()
    titulo = titulo.lower()
    if titulo not in indices:
        return []
    idx = indices[titulo]
    sim_scores = list(enumerate(similitud_cos[idx].flatten()))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores if i[0] < len(peliculas)]
    return [peliculas[i] for i in movie_indices]


# MÉTODOS QUE CALCULAN LA SIMILITUD DEL COSENO ##########################################
# Método que obtiene las similitudes entre peliculas
def calcular_similitud():
    # Crear una representación de texto de cada película
    peliculas = Pelicula.objects.all()
    descripciones = peliculas.values_list(
        'director__nombre', 'generos__nombre', 'plataforma__nombre')
    descripciones = [' '.join(map(str, desc)) for desc in descripciones]

    # Crear un vector de características para cada película
    vectorizer = TfidfVectorizer()
    matriz_tfidf = vectorizer.fit_transform(descripciones)

    # Calcular la similitud del coseno
    similitud_cos = linear_kernel(matriz_tfidf, matriz_tfidf)

    # Para cada película, obtener las 10 películas más similares
    indices = pd.Series(range(len(peliculas)), index=[
                        pelicula.titulo.lower() for pelicula in peliculas]).drop_duplicates()

    return similitud_cos, indices, peliculas