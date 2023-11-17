from django.contrib import admin
from .models import Pelicula, Puntuacion, Plataforma

# Register your models here.
admin.site.register(Pelicula)
admin.site.register(Puntuacion)
admin.site.register(Plataforma)
