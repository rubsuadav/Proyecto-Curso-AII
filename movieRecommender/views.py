from django.shortcuts import render
from .population import populate


def index(request):
    populate()
    return render(request, 'index.html')
