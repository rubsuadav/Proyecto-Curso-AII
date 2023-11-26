from django.db import models


# El modelo Plataforma es sustitutivo del modelo "Usuario" en el sistema de recomendación
class Plataforma (models.Model):
    nombre = models.CharField(max_length=25)
    descripcion = models.TextField(max_length=1000)
    numero_producciones = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)


class Generos(models.Model):
    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)


class Director(models.Model):
    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)


class Pelicula(models.Model):
    titulo = models.CharField(max_length=100)
    sinopsis = models.TextField(max_length=1000)
    fecha_lanzamiento = models.PositiveIntegerField()
    duracion = models.PositiveSmallIntegerField()  # En minutos
    director = models.ForeignKey(Director, on_delete=models.CASCADE)
    plataforma = models.ForeignKey(
        Plataforma, on_delete=models.CASCADE, related_name="plataformas")
    generos = models.ManyToManyField(Generos)
    puntuaciones = models.ManyToManyField(Plataforma, through='Puntuacion')

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ('titulo',)


class Puntuacion(models.Model):
    puntuacion = models.PositiveSmallIntegerField()
    id_plataforma = models.ForeignKey(
        Plataforma, on_delete=models.SET_NULL, null=True)
    id_pelicula = models.ForeignKey(
        Pelicula, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.puntuacion)

    class Meta:
        ordering = ('id_plataforma', 'id_pelicula')
