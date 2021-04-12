from django.shortcuts import render, redirect
from .forms import RegisterForm
from products.models import Product, CategoryFilter
from khipu.models import Payment
from khipu.views import get_payment_by_id, refound
from django.db.models import Q
import datetime
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# Create your views here.
def register(request):

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        new_user = form.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'],
                                )
        login(request, new_user)
        return redirect('/home/')

    context = {"form": form}

    return render(request, "register/register.html", context)

# Integrar la api de algún servicio de envío

def profile(request):

    products = Product.objects.all()
    selected = "default"

    context = {}

    if request.user.is_superuser:
        # si el stock de un producto es 0, se debe desactivar
        for product in products:
            if product.stock <= 0:
                product.stock_active = False
            else:
                product.stock_active = True
            product.save()
    
    else:
        payments = request.user.payment_set.all()

        payments_parsed = []

        for payment in payments:
            custom = json.loads(payment.custom)
            cart_products = custom['cart_products']

            pay_dict = {
                'cart_products': cart_products,
                'amount': int(payment.amount[:-5]),
                'payment_id': payment.payment_id,
                'payer_email': payment.payer_email,
                'payer_name': payment.payer_name,
            }

            payments_parsed.append(pay_dict)

        context = {"payments": payments_parsed}

    # filtramos los productos a través de su categoría
    categories = CategoryFilter.objects.all()
    
    if request.method == "POST":
        categ_name = request.POST.get('categories')
        selected = categ_name
        
        if categ_name != 'default':
            for categ in categories:
                if categ.name == categ_name:
                    products = categ.product_set.all()

    # agregamos los productos al context para pasárselos al template
    context["products"] = products
    context["categories"] = categories

    # si la cantidad de productos en la lista es 1 manda una señal al template
    if len(products) <= 2:
        one_product = True
        context["one_product"] = one_product

    return render(request, "profile.html", context)

