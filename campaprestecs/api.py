
from django.contrib.auth import authenticate as django_authenticate
from ninja import NinjaAPI, Schema
from ninja.security import HttpBasicAuth, HttpBearer
from typing import List, Optional
from .models import *
import secrets
from datetime import date

myapi = NinjaAPI()


#autenticació d'usuari
# Autenticació bàsica
class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = django_authenticate(username=username, password=password)
        if user:
            # Genera un token simple
            token = secrets.token_hex(16)
            user.auth_token = token
            user.save()
            return token
        return None
 
# Autenticació per Token Bearer
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = Usuari.objects.get(auth_token=token)
            return user
        except Usuari.DoesNotExist:
            return None
 
# Endpoint per obtenir un token, accés amb BasicAuth
# amb o sense "trailing slash"
@myapi.get("/token", auth=BasicAuth())
@myapi.get("/token/", auth=BasicAuth())

def obtenir_token(request):
    return {"token": request.auth}


#definicions de prova
@myapi.get("/add")
def add(request, a: int, b: int):
	return {"result": a + b}

@myapi.get("/test")
def test(request):
	return {"result": 33}

#TODO Afegir atributs del model
class PrestecOut(Schema):
	professor_origen :str
	professor_destino: str
	alumne : str
	ordinador: str
	

@myapi.get("/prestec", response=List[PrestecOut], auth=BasicAuth())
def prestec(request):
	prestecs = Prestec.objects.all()
	return prestecs