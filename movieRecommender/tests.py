from django.test import TestCase, RequestFactory, Client
from django.http import HttpRequest
from .views import *
from .models import *
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
import re


class IndexMethodTest(TestCase):
    def test_renderizar_pagina_principal(self):
        response = index(HttpRequest())

        self.assertTrue(response.content.decode(
            'utf8').startswith('<!DOCTYPE html>'))
        self.assertEqual(response.status_code, 200)


class CargarRedireccionMethodTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.factory = RequestFactory()
        self.client = Client()

    def test_redirigir_usuario_pagina_inicio(self):
        request = self.factory.get('/cargar/')
        request.user = self.user

        response = cargar(request)
        contenido = response.content.decode('utf8')

        s1 = BeautifulSoup(contenido, 'lxml')

        self.client.login(username='testuser', password='12345')
        response2 = self.client.post('/cargar/', {'cargar': 'No'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s1.h4.text.strip(),
                         "Carga de la Base de Datos. Confirmación")

        self.assertEqual(response2.status_code, 302)


# CLASE AUXILIAR PARA REFACTORIZAR EL SETEO INICIAL DE LA CARGA DE LA BBDD
class CargarBaseDatosTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.client.post('/cargar/', {'cargar': 'Si'})


# MÉTODO AUXILIAR PARA REFACTORIZAR EL TRATAMIENTO DE DATOS DE LA PAGINA
def tratamiento_datos_scrapping(textos):
    textos = [textos[i].text.strip().replace("\n", "").replace(" ", "").split(":")[j]
              for i in range(3) for j in range(2)]

    return textos[0], textos[1], textos[2], textos[3], textos[4], textos[5]

###########################################################################


class PeliculasMasPopularesMethodTest(CargarBaseDatosTest):
    def test_datos_leidos_correctamente(self):
        self.assertTrue(Pelicula.objects.filter(titulo='X').exists())

    def test_renderizar_peliculas_mas_populares(self):
        request = self.factory.get('/peliculasmaspopulares/')
        request.session = {}

        response = peliculas_mas_populares(request)
        contenido = response.content.decode('utf8')

        s1 = BeautifulSoup(contenido, 'lxml')
        url = s1.header.div.nav.find_all("a")[7]["href"]

        response2 = self.client.get(url)
        contenido2 = response2.content.decode('utf8')

        s2 = BeautifulSoup(contenido2, 'lxml')
        textos = s2.h4.find_next_sibling().find(
            "div", class_="container").find_all("p")

        tt, t, tc, c, td, d = tratamiento_datos_scrapping(textos)

        if "M" in c:
            c = int(c.replace("M", ""))*1000000
        elif "K" in c:
            c = int(c.replace("k", ""))*1000
        elif c:
            c = int(c)

        director = re.sub(r'([a-z])([A-Z])', r'\1 \2', d)

        pelicula = Pelicula.objects.filter(director__nombre=director)[1]

        self.assertEqual(response2.status_code, 200)

        self.assertEqual(tt, "Título")
        self.assertEqual(tc, "Calificación")
        self.assertEqual(td, "Director")

        self.assertTrue(pelicula.generos.all().exists())

        self.assertEqual(t, pelicula.titulo)
        self.assertEqual(c, pelicula.calificacion)
        self.assertEqual(director, pelicula.director.nombre)
