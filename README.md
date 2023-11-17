Sistema de Recomendacion de peliculas de miedo basada en la asignatura de AII

# Instalación

Para instalar las librerias necesarias para el funcionamiento del programa, ejecutar el siguiente comando:

```
pip install -r requirements.txt
```

# Ejecución (SE DEBE DE ABRIR 2 TERMINALES (UNA PARA ACTIVAR TAILWINDCSS Y OTRA PARA EJECUTAR EL SERVIDOR))

Para ejecutar la aplicacion se deben de seguir estos pasos:

0. Instalar Nodejs (NECESARIO SI NO LO TIENES INSTALADO), si lo tienes instalado omita este paso.

Visite esta página para instalarlo

https://nodejs.org/en (INSTALARLO EN LA RUTA POR DEFECTO (C:\Program Files\nodejs\), DEJAR POR DEFECTO LAS OPCIONES DE INSTALACION)

1. Instalar taiwlindcss (DEBES DE TENER NODEJS INSTALADO, RECOMENDADO VERSION LTS 20.9.0), si NO tienes Nodejs instalado vea paso 0 para instalarlo, una vez instalado Nodejs ejecutar el siguiente comando:

```
python manage.py start_styles
```

2. Ejecutar las migraciones de la base de datos

```
python manage.py makemigrations
python manage.py migrate
```

3. Ejecutar el servidor

```
python manage.py runserver
```
