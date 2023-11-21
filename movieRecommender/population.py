# Whoosh imoprts
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.index import open_dir, create_in, exists_in
from whoosh.query import Every, And
from whoosh.fields import *

# BeautifulSoup imports
from bs4 import BeautifulSoup

# Models imports
from .models import Plataforma, Pelicula, Puntuacion

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


def populate():
    # borrar tablas
    Plataforma.objects.all().delete()
    Pelicula.objects.all().delete()
    Puntuacion.objects.all().delete()

    plataformas = []  # Listado de plataformas que se utilizará para el bulk_create
    peliculas = []  # Listado de peliculas
    peliculas2 = []  # Listado de peliculas para el bulk_create
    puntuaciones = []  # Listado de puntuaciones para el bulk_create
    # Diccionario {nombreplataforma:listapeliculas} (para rellenar la FK de pelicula)
    plataformas_peliculas = {}
    dictplataformas = {}  # Diccionario {nombreplataforma:objetoplataforma}
    dictpeliculas = {}  # Diccionario {idpelicula:objetopelicula}
    pl = 1  # Id para la plataforma
    p = 1  # Id para la pelicula
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
        nombre_plataforma = dp.img["title"]
        enlace_plataforma = dp.a["href"]

        if nombre_plataforma not in dictplataformas.keys():
            s4 = permission_to_scrap(enlace_plataforma)

            # Datos específicos de la plataforma
            descripcion = s4.find(
                "div", class_=re.compile("content-header")).find_all("div")[2].find_next("div").text.strip()
            numero_producciones = s4.find(
                "div", class_=re.compile("title-list")).find("div", class_="total-titles-seo").text.strip().replace("títulos", "")

            # Agregamos la plataforma a la lista de plataformas
            objeto_plataforma = Plataforma(
                id=pl, nombre=nombre_plataforma, descripcion=descripcion, numero_producciones=numero_producciones)
            plataformas.append(objeto_plataforma)
            dictplataformas[nombre_plataforma] = objeto_plataforma
            pl += 1

        # CARGAR DATOS DE LAS PELICULAS #
        # nos quedamos con las plataformas que tienen peliculas --> 61 plataformas con peliculas
        if s4.find("div", {'listlayout': 'grid'}) is not None:
            datos2 = s4.find("div", {'listlayout': 'grid'}).find(
                "div", class_="title-list-grid").find_all("div", class_="title-list-grid__item")
            # como no hay paginacion y carga todas las peliculas de las 61 plataformas (mas de 1000 en total),
            # limitamos la carga de aproximadamente 400 peliculas para que no tarde tanto,
            # para saber con cuantas nos quedamos por plataformas dividimos 400 entre 61
            # con 6 salen 366 peliculas y con 7 salen 427 asi que nos quedamos con 7
            for d in datos2[:7]:
                if d.a is not None:
                    s5 = permission_to_scrap(d.a["href"])
                    datos3 = s5.find("div", class_="jw-info-box")

                    if datos3 is not None:
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

                        # Obtenemos el género, el director y la duración
                        datos4 = datos3.find(
                            "div", class_="title-info").find_all("div", class_="detail-infos")
                        for d4 in datos4:
                            etiquetas_iguales = d4.find(
                                "h3", class_="detail-infos__subheading")  # los 3 atribs tienen misma etiqueta
                            if etiquetas_iguales.text.strip() == "Géneros":
                                generos = etiquetas_iguales.find_next_sibling(
                                    "div").text.strip()  # tambien equivalente d4.div.text.strip()

                        # BOCETO DE ALMACENAMIENTO DE FK (COMPROBAR BOCETO DE FK)
                        """objeto_pelicula = (
                                (p, titulo, "sinopsis", "genero", "director",  2019, 120, dictplataformas[nombre_plataforma]))
                            dictpeliculas[p] = objeto_pelicula
                            p += 1
                            peliculas.append(objeto_pelicula)

                            # Completamos el diccionario de las plataformas y sus peliculas.
                            # Si el nombre de la plataforma ya es una clave, cojo su valor (lista) y le añado la nueva pelicula
                            # En caso contrario, añado una nueva clave que sea el nombre de la plataforma, y le añado la pelicula (lista)
                            if nombre_plataforma in plataformas_peliculas:
                                listpelis = plataformas_peliculas[nombre_plataforma]
                                listpelis.append(objeto_pelicula)
                                plataformas_peliculas[nombre_plataforma] = listpelis
                            else:
                                plataformas_peliculas[nombre_plataforma] = [
                                    objeto_pelicula]"""

    # Almacenamos las plataformas en la BBDD
    Plataforma.objects.bulk_create(plataformas)
    print("Plataformas almacenadas")

    """# Almacenamos las peliculas en la BBDD
    for pp in plataformas_peliculas:
        pelis = plataformas_peliculas[pp]
        for pe in pelis:
            objeto_pelicula = Pelicula(
                id=pe[0], titulo=pe[1], sinopsis=pe[2], genero=pe[3], director=pe[4], fecha_lanzamiento=pe[5], duracion=pe[6], plataforma=pe[7])
            peliculas2.append(objeto_pelicula)

    Pelicula.objects.bulk_create(peliculas2)
    print("Peliculas almacenadas")"""
