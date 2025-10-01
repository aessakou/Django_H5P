from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Django</h1><p>This is the default root page.</p>")


urlpatterns = [
	path('', home)
]