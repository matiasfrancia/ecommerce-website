from django.shortcuts import render, reverse, redirect
import json
from products.models import Product
from google_currency import convert

from khipu.models import Payment
from khipu.views import get_payment_by_id

from .PayPalRequest import CreateOrder
from django.http import JsonResponse
from khipu.forms import KhipuCreatePaymentForm
import datetime

# ========================================================== Cart ==========================================================
def cart_view(request):

    # elimina el carro de compras en caso de que el pago esté hecho y actualiza el estado del pago en la base de datos
    # TODO: hacer una función async que cargue el template sólo si se completo la petición

    # obtenemos las cookies con el id

    items = []
    total_price = 0
    payment_ready = False

    try:
        payment_id = request.COOKIES.get('pi')
        print("Paymend ID: ", payment_id)
        if payment_id != '':
            get_payment_by_id(payment_id)

            # comprobamos si el pago fue realizado
            payment = Payment.objects.get(payment_id=payment_id)

            print("Payment status: ", payment.status)
            if payment.status == 'done':
                payment_ready = True
    except:
        print("Except")

    items, total_price = get_cart(request)

    context = {"items":items, "total_price": total_price, "payment_ready": payment_ready}
    
    return render(request, "cart.html", context)

    # y acá se debe eliminar el id de las cookies, para que no borre los productos del carro cuando se quiera comprar algo más

def get_cart(request, to_json = False):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {"orden": []}

    items = []
    total_price = 0

    for product_id in cart['orden']:

        product = Product.objects.get(id=product_id)
        quantity = abs(int(cart[product_id]['cantidad']))

        if quantity > product.stock:
            quantity = product.stock

        if quantity == 0:
            quantity = 1

        if not to_json:
            item = {
                "product": product,
                "quantity": quantity,
                "subtotal": quantity * product.price,
            }
        else:
            item = {
                "product_title": product.title,
                "product_id": product.id,
                "product_quantity": quantity,
                "subtotal": quantity * product.price,
            }

        if product.active and product.stock_active:
            items.append(item)
            total_price += item['subtotal']

    return (items,total_price)

# ========================================================== PayPal ==========================================================

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

# ========================================================== GooglePay ==========================================================

def googlepay_API(requset):
    if request.method == 'POST':
        items,total_price = get_cart(request)
        return JsonResponse({"total":total_price})
    else:
        return JsonResponse({"details":"invalid request"})

def convert_clp_to_usd(price):
    string_price = convert('clp', 'usd', price)
    json_price = json.loads(string_price)
    return json_price

# ========================================================== Khipu ==========================================================

def khipu_API(request):

    # cart_products: lista item = [{'product', 'quantity', 'subtotal'}, ...]
    cart_products, cart_total = get_cart(request, True)

    dicc_custom = {"cart_products": cart_products}
    json_custom = json.dumps(dicc_custom)

    """ cart_string = ""

    for item in cart_products:
        # TODO: pasar también el id del producto
        cart_string += item['product'].title + ":" + str(item['quantity']) + "&&"

    cart_string = cart_string[:-2] """

    # Obtenemos la fecha de expiración
    now = datetime.datetime.today()

    expires_date = now + datetime.timedelta(hours=12)
    expires_date = expires_date.replace(microsecond=0).isoformat() + 'Z'

    # Hace la llamada a khipu

    form_payment_khipu = KhipuCreatePaymentForm(**{
        # tenemos que vaciar el carro una vez que se completa el pago
        'subject': 'Esto es un pago de pruebas via Django-Form',
        'currency': 'CLP',
        'amount': str(cart_total) + '.0000',
        'return_url': request.build_absolute_uri(reverse('cart:cart_view')),
        'custom': json_custom,
        'expires_date': expires_date,
    })

    # obtenemos el objeto del pago a través del id
    payment_id = form_payment_khipu.return_id()

    payment = Payment.objects.get(payment_id=payment_id)
    request.user.payment_set.add(payment)

    return render(request, 'khipu.html', {'form_payment_khipu': form_payment_khipu})