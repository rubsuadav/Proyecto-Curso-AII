from django.contrib import admin
from .models import Pelicula, Plataforma, Generos, Director

# Register your models here.
admin.site.register(Pelicula)
admin.site.register(Plataforma)
admin.site.register(Generos)
admin.site.register(Director)
