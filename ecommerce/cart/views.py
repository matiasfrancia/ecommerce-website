from django.shortcuts import render
import json
from products.models import Product
from .PayPalRequest import CreateOrder
from django.http import JsonResponse

# Cuando se borra un producto de la base de datos también se debe borrar del carro de compras

# Create your views here.
def cart_view(request):

    items,total_price = get_cart(request)
    print(items,total_price)
    context = {"items":items, "total_price": total_price}
    return render(request, "cart.html", context)

def paypal(request):
    return render(request, "paypal.html")

def paypal_API(request):
    if request.method == 'POST':
        items,total_price = get_cart(request)
        order = CreateOrder().create_order(total_price)
        data = order.result.__dict__['_dict']
        return JsonResponse(data)
    else:
        return JsonResponse({"details":"invalid request"})

def googlepay_API(requset):
    if request.method == 'POST':
        items,total_price = get_cart(request)
        return JsonResponse({"total":total_price})
    else:
        return JsonResponse({"details":"invalid request"})

def get_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print("cart",cart)
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

    print(items,total_price)
    return (items,total_price)