from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import *

@login_required
def get_prestecs(request):
    jsonData = list( Prestec.objects.all().values() )
    return JsonResponse({
            "status": "OK",
            "questions": jsonData,
        }, safe=False)

# Create your views here.
@login_required
def prova_auth(request):
	return HttpResponse("usuari: "+str(request.user))