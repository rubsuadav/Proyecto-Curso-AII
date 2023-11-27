from django.shortcuts import render
from .population import populateDB
from .models import Pelicula, Director, Puntuacion, Generos, Plataforma


def index(request):
    return render(request, 'index.html', {'peliculas': Pelicula.objects.all(), 'directores': Director.objects.all(), 'puntuaciones': Puntuacion.objects.all(), 'generos': Generos.objects.all(), 'plataformas': Plataforma.objects.all()})
