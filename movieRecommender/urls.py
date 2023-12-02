from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # AGRUPACIONES DE PELÍCULAS POR ATRIBUTOS
    path('peliculasagrupadasporplataforma/',
         views.peliculas_agrupadas_por_plataforma, name='agrupacion1'),
    path('peliculasagrupadasporgenero/',
         views.peliculas_agrupadas_por_genero, name='agrupacion2'),

    # DETALLES
    path('peliculas/<int:pelicula_id>/',
         views.detalles_pelicula, name='detalles_pelicula'),

    # BÚSQUEDAS DE PELÍCULAS POR ATRIBUTOS
    path('buscar/', views.buscar, name='buscar'),

    # GESTION DE USUARIOS
    path('registro/', views.register, name='registro'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_session, name='logout'),

    # CARGAR DATOS
    path('cargar/', views.cargar, name='cargar'),
    # path('cargarSR/', views.loadRS, name='cargarSR')
]
