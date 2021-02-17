from django.shortcuts import render
import json
from products.models import Product

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
