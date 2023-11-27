from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.register, name='registro'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_session, name='logout'),
    path('cargar/', views.cargar, name='cargar'),
    path('cargarSR/', views.loadRS, name='cargarSR')
]
