from django.shortcuts import render
import json
from products.models import Product
from .PayPalRequest import CreateOrder
from django.http import JsonResponse

# Create your views here.
def Cart(request):

    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    for i in cart:
        product = Product.objects.get(id=i)
        item = {
            "product": product,
            "quantity": cart[i]['cantidad']
        }
        items.append(item)

    context = {"items":items}
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
        