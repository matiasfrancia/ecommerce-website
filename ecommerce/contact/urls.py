from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.contact, name = 'contact'),
]