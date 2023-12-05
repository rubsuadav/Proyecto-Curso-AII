from django.test import TestCase, RequestFactory, Client
from django.http import HttpRequest
from .views import *
from .models import *
from bs4 import BeautifulSoup
from django.contrib.auth.models import User


class IndexMethodTest(TestCase):
    def test_renderizar_pagina_principal(self):
        response = index(HttpRequest())
        contenido = response.content.decode('utf8')

        self.assertTrue(contenido.startswith('<!DOCTYPE html>'))
        self.assertEqual(response.status_code, 200)


class CargarMethodTest(TestCase):
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
        texto = s1.h4.text.strip()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(texto, "Carga de la Base de Datos. Confirmación")

        self.client.login(username='testuser', password='12345')
        data2 = {'cargar': 'No'}

        response2 = self.client.post('/cargar/', data2)
        self.assertEqual(response2.status_code, 302)


class MostPopularMoviesMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.factory = RequestFactory()
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        data = {'cargar': 'Si'}
        self.client.post('/cargar/', data)

    def test_datos_leidos_correctamente(self):
        data_loaded = Pelicula.objects.filter(titulo='X').exists()
        self.assertTrue(data_loaded)

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
        texto = s2.h4.find_next_sibling().find(
            "div", class_="container").p.text.strip()

        self.assertEqual(response2.status_code, 200)
        self.assertEqual(texto, "Título")
