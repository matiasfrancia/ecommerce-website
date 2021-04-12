from django.shortcuts import render, reverse, redirect
import json
from products.models import Product
from payment.views import enter_movements_payment, payment_status_update_by_id, \
                        save_payment_id, get_payment_id, delete_payment_id

from . import api as cart_api

from khipu.models import Payment

from django.http import JsonResponse
from khipu.forms import KhipuCreatePaymentForm
import datetime

# ========================================================== Cart ==========================================================

def cart_view(request):

    # obtenemos las cookies con el id

    items = []
    total_price = 0

    try:
        payment_id = get_payment_id(request)
        if payment_id != None:
            payment_status_update_by_id(request, payment_id)

    except:
        print("Hubo un error al actualizar el pago (view del carro de compras)")

    # elimina producto del carrito
    if request.method == "POST":

        print(request.POST)

        for posted in request.POST:
            if 'quantity' in posted:
                product_id = int(posted.replace('quantity', ''))
                new_quantity = int(request.POST[posted])

                cart_api.set_quantity(request, product_id, new_quantity)

        remove = request.POST.get('removeItem')

        if remove:
            id_product = int(remove.replace('removeItem', ''))
            cart_api.delete_element(request, id_product)
        
        print(cart_api.get_cart(request))

    items, total_price = get_parsed_cart(request)

    context = {"items": items, "total_price": total_price}
    
    return render(request, "cart.html", context)

# parsea la información del carrito
def get_parsed_cart(request, to_json = False):

    # envía una alerta en caso de que se exceda del stock máximo
    send_alert = False

    cart = cart_api.get_cart(request)
    if cart == None:
        cart = []

    items = []
    total_price = 0

    for product_id, quantity in cart:

        product = Product.objects.get(id=product_id)

        if quantity > product.stock:
            quantity = product.stock

            # actualiza la cantidad del producto en el carrito según el stock que hay
            cart_api.set_quantity(request, product_id, quantity)
            send_alert = True

        if not to_json:
            item = {
                "product": product,
                "quantity": quantity,
                "subtotal": quantity * product.price,
                "send_alert": send_alert,
                "alert_text": "El stock máximo de<br>" + product.title + " es: " + str(product.stock),
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

# ========================================================== Khipu ==========================================================

def get_expires_date(hours=12):

    now = datetime.datetime.today()

    expires_date = now + datetime.timedelta(hours=hours)
    expires_date = expires_date.replace(microsecond=0).isoformat() + 'Z'

    return expires_date

def khipu_API(request):

    # creamos un pago únicamente si no hay uno ya en las cookies
    payment_id = get_payment_id(request)

    if payment_id == None:

        # cart_products: lista item = [{'product', 'quantity', 'subtotal'}, ...]
        cart_products, cart_total = get_parsed_cart(request, True)

        dicc_custom = {"cart_products": cart_products}
        json_custom = json.dumps(dicc_custom)

        print(dicc_custom)
        print(json_custom)

        # Obtenemos la fecha de expiración
        expires_date = get_expires_date()

        # crea el fomulario para la conexión con khipu
        form_payment_khipu = KhipuCreatePaymentForm(**{'payment_id': payment_id})

        # se conecta con khipu y crea la instancia de CreatePayment
        form_payment_khipu.khipu_service(**{
            # tenemos que vaciar el carro una vez que se completa el pago
            'subject': 'Esto es un pago de ' + str(request.user),
            'currency': 'CLP',
            'amount': str(cart_total) + '.0000',
            'return_url': request.build_absolute_uri(reverse('payment:payment-detail')),
            'custom': json_custom,
            'expires_date': expires_date,
        })
        
        
        # obtenemos el objeto del pago a través del id
        payment_id = form_payment_khipu.return_id()

        save_payment_id(request, payment_id)

        # si el usuario está registrado, le adjudicamos el pago
        if request.user.is_authenticated:
            payment = Payment.objects.get(payment_id=payment_id)
            request.user.payment_set.add(payment)
        
        # revisa si está la información de despacho en las variables de sesión y las guarda en Payment
        if 'shipping_data' in request.session:
            info = request.session['shipping_data']
            payment = Payment.objects.get(payment_id=payment_id)
            payment.direction = info['direction']
            payment.city = info['city']
            payment.cellphone = info['cellphone']
            payment.save()

    else:
        form_payment_khipu = KhipuCreatePaymentForm(**{'payment_id': payment_id})

    return render(request, 'khipu.html', {'form_payment_khipu': form_payment_khipu, 'payment_id': payment_id})