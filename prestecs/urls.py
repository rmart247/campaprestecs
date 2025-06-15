from django.contrib import admin
from django.urls import path, include

from campaprestecs import views, api

from ninja import NinjaAPI

urlpatterns = [
    #auth routes

    path("accounts/", include("django.contrib.auth.urls")),
    #path("accounts/profile/", profile, name="profile"),

    #admin
    path('admin/', admin.site.urls),
    path('prova_auth', views.prova_auth ),

    #Api manual (sense plugins)
    path('api/get_prestecs', views.get_prestecs, name='get_prestecs'),

    #api ninja
    path("api/", api.myapi.urls),
]
