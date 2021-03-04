from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name = 'cart_view'),
    path('paypal',views.paypal, name = 'paypal'),
    path('googlepay',views.googlepay_API, name = 'googlepayAPI'),
    path('pay',views.paypal_API, name = 'paypalAPI'),
    path("khipuAPI/", views.khipu_API, name="khipuAPI"),
]