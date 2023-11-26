from django.shortcuts import render
from .population import populateDB


def index(request):
    populateDB()
    return render(request, 'index.html')
