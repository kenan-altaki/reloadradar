# Third Party Libraries
from core.models import Manufacturer

# Django Libraries
from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, "core/home.html", None)


def propellant_overview(request):
    context = {"manufacturers": [m for m in Manufacturer.objects.all()]}

    return render(request, "core/overview.html", context)