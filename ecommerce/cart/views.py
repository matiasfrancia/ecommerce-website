from django.shortcuts import render
import json
from products.models import Product
from .PayPalRequest import CreateOrder
from django.http import JsonResponse

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

    context = {"items":items, "total_price": total_price}
    return render(request, "cart.html", context)

def PayPal(request):
    return render(request, "paypal.html")

def Pagar(request):
    if request.method == 'POST':
        order = CreateOrder().create_order(debug=True)
        data = order.result.__dict__['_dict']
        return JsonResponse(data)
    else:
        return JsonResponse({"details":"invalid request"})