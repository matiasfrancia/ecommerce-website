from django.shortcuts import render, redirect
from products.models import Product

def home(request):

    products = Product.objects.all()

    return render(request, "index.html", {"ps": products})