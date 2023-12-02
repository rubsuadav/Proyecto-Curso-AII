# Generated by Django 4.2.7 on 2023-12-02 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Director',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25)),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Generos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25)),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Plataforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25)),
                ('descripcion', models.TextField(max_length=1000)),
                ('numero_producciones', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Pelicula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('sinopsis', models.TextField(max_length=1000)),
                ('fecha_lanzamiento', models.PositiveIntegerField()),
                ('duracion', models.PositiveSmallIntegerField()),
                ('imagen', models.URLField()),
                ('director', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movieRecommender.director')),
                ('generos', models.ManyToManyField(to='movieRecommender.generos')),
                ('plataforma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plataformas', to='movieRecommender.plataforma')),
            ],
            options={
                'ordering': ('titulo',),
            },
        ),
    ]
