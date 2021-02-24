from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name = 'cart'),
    path('paypal',views.PayPal, name = 'paypal'),
    path('pay',views.Pagar, name = 'pagar'),
]