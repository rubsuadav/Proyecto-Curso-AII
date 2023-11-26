# Whoosh imoprts
from whoosh.index import create_in
from whoosh.fields import *

# BeautifulSoup imports
from bs4 import BeautifulSoup

# Models imports
from .models import Plataforma, Pelicula, Puntuacion, Generos, Director

# Others imports
import os
import urllib.request
import ssl
import shutil
import re
import numpy
import urllib.error
import time

# lineas para evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# MÉTODO AUXILIAR PARA SOLUCIONAR EL ERROR 403 DE PERMISO DE SCRAPPING DE LA WEB
def permission_to_scrap(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'es'}
    request = urllib.request.Request(
        "https://www.justwatch.com" + url, headers=headers)

    # Algunas veces da error 429 de más peticiones de las permitidas
    # por lo que agregamos un tiempo de espera para evitarlo
    tiempo_espera = 1
    while True:
        try:
            f = urllib.request.urlopen(request)
            return BeautifulSoup(f, 'lxml')
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(
                    f"Error 429: Demasiadas solicitudes. Esperando {tiempo_espera} segundos.")
                time.sleep(tiempo_espera)
                tiempo_espera += 1


def upload_plataformas(dp):
    nombre_plataforma = dp.img["title"]
    enlace_plataforma = dp.a["href"]
    s4 = permission_to_scrap(enlace_plataforma)

    # Datos específicos de la plataforma
    descripcion = s4.find(
        "div", class_=re.compile("content-header")).find_all("div")[2].find_next("div").text.strip()
    numero_producciones = s4.find(
        "div", class_=re.compile("title-list")).find("div", class_="total-titles-seo").text.strip().replace("títulos", "")

    # insertar datos en la base de datos
    plataforma, created = Plataforma.objects.get_or_create(
        nombre=nombre_plataforma, descripcion=descripcion, numero_producciones=numero_producciones)

    return s4, plataforma, created


def upload_data_peliculas(datos3):
    titulo = datos3.find(
        "div", class_="title-block").h1.text.strip()
    fecha = datos3.find(
        "div", class_="title-block").span.text.strip()[1:-1]  # Quitamos los paréntesis
    sinopsis = datos3.find(
        'div', class_='streaming-chart').find_next_sibling()
    if sinopsis is not None:
        sinopsis = sinopsis.find_all("p")
        for si in sinopsis:
            sinopsis = si.text.strip()
    else:
        sinopsis = "No hay sinopsis disponible"

    return titulo, fecha, sinopsis


def upload_generos(etiquetas_iguales, lista_generos):
    generos_etiq = etiquetas_iguales.find_next_sibling(
        "div")
    if generos_etiq.text.strip() != "":
        generos = "".join(
            generos_etiq.stripped_strings)
        # Dividir la cadena de generos en una lista de generos
        generos = [genero.strip()
                   for genero in generos.split(",")]
        lista_generos += generos
    else:
        lista_generos.append("No disponible")

    return lista_generos


def upload_duración(etiquetas_iguales):
    duracion_horas_minutos = etiquetas_iguales.find_next_sibling(
        "div").text.strip()  # tambien equivalente d4.div.text.strip()
    if "h" in duracion_horas_minutos:
        duracion = int(duracion_horas_minutos.split(
            "h")[0]) * 60 + int(duracion_horas_minutos.split("h")[1].split("min")[0])
    else:
        duracion = int(
            duracion_horas_minutos.split("min")[0])

    return duracion


def populateDB():
    # borrar tablas
    Plataforma.objects.all().delete()
    Pelicula.objects.all().delete()
    Puntuacion.objects.all().delete()
    Generos.objects.all().delete()
    Director.objects.all().delete()

    puntuaciones = []  # Listado de puntuaciones para el bulk_create
    pun = 1  # Id para la puntuación

    s = permission_to_scrap("")

    datos = s.find("div", class_="content").find(
        "div", class_="content__providers").find("button", class_="content__providers__see-all").find_previous("a")["href"]

    s2 = permission_to_scrap(datos)

    # JustWatch nos muestra tantos las peliculas como las series, por lo que nos quedamos solo con las peliculas
    enl = s2.find("div", class_="filter-bar-seo").find_all("div",
                                                           class_="filter-bar-content-type__item")[1].a["href"]
    s3 = permission_to_scrap(enl)

    # CARGAR DATOS DE LAS PLATAFORMAS #
    datos_plataformas = s3.find(
        "div", class_=re.compile("__items")).find_all("div")

    for dp in datos_plataformas:  # 69 plataformas en total
        s4, plataforma, created = upload_plataformas(dp)

        # CARGAR DATOS DE LAS PELICULAS #
        # nos quedamos con las plataformas que tienen peliculas --> 61 plataformas con peliculas
        if s4.find("div", {'listlayout': 'grid'}) is not None:
            datos2 = s4.find("div", {'listlayout': 'grid'}).find(
                "div", class_="title-list-grid").find_all("div", class_="title-list-grid__item")
            # como no hay paginacion y carga todas las peliculas de las 61 plataformas (mas de 1000 en total),
            # limitamos la carga de aproximadamente 250 peliculas para que no tarde tanto,
            # para saber con cuantas nos quedamos por plataformas dividimos 250 entre 61
            # con 4 nos salen 244 peliculas y con 5 salen 305 asi que nos quedamos con 4
            for d in datos2[:4]:
                if d.a is not None:
                    s5 = permission_to_scrap(d.a["href"])
                    datos3 = s5.find("div", class_="jw-info-box")

                    if datos3 is not None:
                        titulo, fecha, sinopsis = upload_data_peliculas(datos3)
                        lista_generos = []

                        # Obtenemos los géneros, el director y la duración
                        datos4 = datos3.find(
                            "div", class_="title-info").find_all("div", class_="detail-infos")
                        for d4 in datos4:
                            etiquetas_iguales = d4.find(
                                "h3", class_="detail-infos__subheading")  # los 3 atribs tienen misma etiqueta

                            if etiquetas_iguales.text.strip() == "Géneros":
                                generos = upload_generos(
                                    etiquetas_iguales, lista_generos)

                            if etiquetas_iguales.text.strip() == "Duración":
                                duracion = upload_duración(
                                    etiquetas_iguales)

                            if etiquetas_iguales.text.strip() == "Director":
                                nombre_director = etiquetas_iguales.find_next_sibling(
                                    "div").text.strip()  # tambien equivalente d4.div.text.strip()

                                # insertar datos en la base de datos
                                director, created = Director.objects.get_or_create(
                                    nombre=nombre_director)

                    # insertar datos en la base de datos
                    pelicula, created = Pelicula.objects.get_or_create(
                        titulo=titulo, sinopsis=sinopsis, fecha_lanzamiento=fecha, duracion=duracion, director=director, plataforma=plataforma)

                    # Crear o recuperar cada género individualmente
                    for nombre_genero in generos:
                        genero, created = Generos.objects.get_or_create(
                            nombre=nombre_genero)
                        # añadir géneros a la pelicula
                        pelicula.generos.add(genero)

    # Crear esquema de las peliculas
    print("Creando esquema de las peliculas...")
    create_shema_peliculas()

    # CARGAR DATOS DE LAS PUNTUACIONES #
    puntuaciones_posibles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    peliculas = Pelicula.objects.all()
    for plataforma in Plataforma.objects.all():
        # Una plataforma no puede puntuarse a sí misma
        lista_peliculas = [
            p for p in peliculas if p.plataforma.id != plataforma.id]
        peliculas_elejidas = numpy.random.choice(
            lista_peliculas, 10, replace=False)
        peliculas_puntuadas = zip(puntuaciones_posibles, peliculas_elejidas)
        for pp in peliculas_puntuadas:
            puntuaciones.append(Puntuacion(
                id=pun, puntuacion=pp[0], id_plataforma=plataforma, id_pelicula=pp[1]))
            pun += 1

    # Insertar las puntuaciones en la base de datos
    Puntuacion.objects.bulk_create(puntuaciones)
    print("Puntuaciones cargadas correctamente")

    return True


def create_shema_peliculas():
    shema = Schema(id=NUMERIC(stored=True), titulo=TEXT(
        stored=True), sinopsis=TEXT(stored=True), fecha_lanzamiento=NUMERIC(stored=True), duracion=NUMERIC(stored=True), director=NUMERIC(stored=True), plataforma=NUMERIC(stored=True), generos=KEYWORD(stored=True, commas=True))

    if os.path.exists("indice_peliculas"):
        shutil.rmtree("indice_peliculas")
    os.mkdir("indice_peliculas")

    ix = create_in("indice_peliculas", shema)
    writer = ix.writer()
    lista_peliculas = Pelicula.objects.all()

    for pelicula in lista_peliculas:
        generos = ','.join([str(genero) for genero in pelicula.generos.all()])
        writer.add_document(id=pelicula.id, titulo=pelicula.titulo, sinopsis=pelicula.sinopsis, fecha_lanzamiento=pelicula.fecha_lanzamiento,
                            duracion=pelicula.duracion, director=pelicula.director.id, plataforma=pelicula.plataforma.id, generos=generos)
    writer.commit()
