from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('peliculasmaspopulares/',
         views.peliculas_mas_populares, name='pelis_populares'),

    # AGRUPACIONES DE PELÍCULAS POR ATRIBUTOS
    path('peliculasagrupadasporplataforma/',
         views.peliculas_agrupadas_por_plataforma, name='agrupacion1'),
    path('peliculasagrupadasporgenero/',
         views.peliculas_agrupadas_por_genero, name='agrupacion2'),

    # DETALLES
    path('peliculas/<int:pelicula_id>/',
         views.detalles_pelicula, name='detalles_pelicula'),
    path('plataformas/<int:plataforma_id>/',
         views.detalles_plataforma, name='detalles_plataforma'),

    # BÚSQUEDAS DE PELÍCULAS POR ATRIBUTOS
    path('buscarpeliculasporgenero/', views.buscar_por_genero, name='busqueda1'),
    path('buscarpeliculasportituloosinopsis/',
         views.buscar_titulo_o_sinopsis, name='busqueda2'),
    path('buscarpeliculasporgeneroytitulo/',
         views.buscar_genero_y_titulo, name='busqueda3'),
    path('buscarpeliculasporfechalanzamiento/',
         views.buscar_fecha_lanzamiento, name='busqueda4'),
    path('buscarpeliculasporgeneroypaisoporpaisysinopsis/',
         views.buscar_genero_y_pais_o_pais_y_sinopsis, name='busqueda5'),

    # GESTION DE USUARIOS
    path('registro/', views.register, name='registro'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_session, name='logout'),

    # CARGAR DATOS
    path('cargar/', views.cargar, name='cargar'),

    # RECOMENDACIONES
    path('recomendacionespeliculasportitulo/',
         views.recomendar_pelicula_segun_titulo, name='recom1'),

]
