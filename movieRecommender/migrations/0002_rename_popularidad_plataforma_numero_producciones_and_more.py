# Generated by Django 4.2.6 on 2023-11-18 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movieRecommender', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plataforma',
            old_name='popularidad',
            new_name='numero_producciones',
        ),
        migrations.RemoveField(
            model_name='plataforma',
            name='precio_mensual',
        ),
    ]