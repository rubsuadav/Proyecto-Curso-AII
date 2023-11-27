from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import shelve

from .population import populateDB
from .recommendations import transformPrefs, calculateSimilarItems
from .models import Pelicula, Director, Puntuacion, Generos, Plataforma


def index(request):
    return render(request, 'index.html', {'peliculas': Pelicula.objects.all(), 'directores': Director.objects.all(), 'puntuaciones': Puntuacion.objects.all(), 'generos': Generos.objects.all(), 'plataformas': Plataforma.objects.all()})


# Cargar sistema de Recomendacion
def loadDict():
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


@login_required(login_url='index')
def loadRS(request):
    if request.method == 'POST':
        if 'Aceptar' in request.POST:
            loadDict()
            mensaje = "Se ha cargado el sistema de recomendación correctamente"
            return render(request, 'cargar_SR.html', {'mensaje': mensaje})
        else:
            return redirect("index")
    return render(request, 'confirmar_SR.html')
