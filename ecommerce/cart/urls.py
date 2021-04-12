from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name = 'cart_view'),
    path("khipuAPI/", views.khipu_API, name="khipuAPI"),
]