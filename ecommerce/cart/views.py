from django.shortcuts import render
import json
from products.models import Product
from google_currency import convert
import json

# Cuando se borra un producto de la base de datos también se debe borrar del carro de compras

# Create your views here.
def cart_view(request):

    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    total_price = 0

    for i in cart:

        product = Product.objects.get(id=i)
        quantity = abs(int(cart[i]['cantidad']))

        if quantity == 0:
            quantity = 1

        item = {
            "product": product,
            "quantity": quantity,
            "subtotal": quantity * product.price,
        }

        items.append(item)
        total_price += item['subtotal']

    total_price_usd = convert_clp_to_usd(total_price)['amount']

    context = {"items":items, "total_price": total_price}

    return render(request, "cart.html", context)

def convert_clp_to_usd(price):
    string_price = convert('clp', 'usd', price)
    json_price = json.loads(string_price)
    return json_price