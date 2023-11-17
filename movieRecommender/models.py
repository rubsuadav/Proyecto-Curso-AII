from django.db import models

# Create your models here.
# Representa los generos de las películas


"""class Categoria(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)"""


# Representa los medios de comunicación que lanzan las peliculas
"""class Medio(models.Model):
    nombre = models.CharField(max_length=30)  # empresas que lanzan la pelicula
    pais = models.CharField(max_length=25)  # pais de origen de la pelicula
    # fecha de lanzamiento de la pelicula
    lanzamiento = models.CharField(max_length=100)

    def __str__(self):
        return "Lanzado en " + self.pais + " el " + str(self.lanzamiento) + " por " + self.nombre

    class Meta:
        ordering = ('pais',)"""


# Representa las películas
class Pelicula(models.Model):
    titulo = models.CharField(max_length=40)
    descripcion = models.TextField()
    duracion = models.PositiveIntegerField()  # Duración en minutos
    clasificacion = models.CharField(max_length=10)
    genero = models.CharField(max_length=200)
    empresas_lanzamiento = models.CharField(max_length=200)
    pais_origen = models.CharField(max_length=200)
    fecha_lanzamiento = models.CharField(max_length=200)
    # puntuaciones = models.ManyToManyField(Medio, through='Puntuacion')

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ('titulo',)


# Representa las puntuaciones que se le dan a las películas por los medios de comunicación
class Puntuacion(models.Model):
    puntuacion = models.PositiveSmallIntegerField()
    # id_medio = models.ForeignKey(Medio, on_delete=models.SET_NULL, null=True)
    id_pelicula = models.ForeignKey(
        Pelicula, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (str(self.puntuacion))

    class Meta:
        ordering = ('id_pelicula',)
