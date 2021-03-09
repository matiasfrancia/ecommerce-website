from django.shortcuts import render, reverse, redirect
import json
from products.models import Product
from register.views import enter_movements_payment
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
        if payment_id != '':
            get_payment_by_id(payment_id)

            # comprobamos si el pago fue realizado
            payment = Payment.objects.get(payment_id=payment_id)

            print("Payment status: ", payment.status)

            if payment.status == 'done':
                payment_ready = True
                if 'shipping_data' in request.session:
                    del request.session['shipping_data']
                    
                # descontar del stock las nuevas compras realizadas
                negatives_stocks = enter_movements_payment('salida', payment)
                
                # agregamos negatives_stocks a las variables de sesión si != []
                if negatives_stocks != []:
                    request.session[id] = {'negatives_stocks': negatives_stocks}

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

    # creamos un pago únicamente si no hay uno ya en las cookies
    payment_id = request.COOKIES.get('pi')

    if not payment_id:

        # cart_products: lista item = [{'product', 'quantity', 'subtotal'}, ...]
        cart_products, cart_total = get_cart(request, True)

        dicc_custom = {"cart_products": cart_products}
        json_custom = json.dumps(dicc_custom)

        # Obtenemos la fecha de expiración
        now = datetime.datetime.today()

        expires_date = now + datetime.timedelta(hours=12)
        expires_date = expires_date.replace(microsecond=0).isoformat() + 'Z'

        # crea el fomulario para la conexión con khipu
        form_payment_khipu = KhipuCreatePaymentForm(**{'payment_id': payment_id})

        # se conecta con khipu y crea la instancia de CreatePayment
        form_payment_khipu.khipu_service(**{
            # tenemos que vaciar el carro una vez que se completa el pago
            'subject': 'Esto es un pago de ' + str(request.user),
            'currency': 'CLP',
            'amount': str(cart_total) + '.0000',
            'return_url': request.build_absolute_uri(reverse('cart:cart_view')),
            'custom': json_custom,
            'expires_date': expires_date,
        })
        
        # obtenemos el objeto del pago a través del id
        payment_id = form_payment_khipu.return_id()

        # si el usuario está registrado, le adjudicamos el pago
        if request.user.is_authenticated:
            payment = Payment.objects.get(payment_id=payment_id)
            request.user.payment_set.add(payment)
        
        if 'shipping_data' in request.session:
            info = request.session['shipping_data']
            print(info)
            payment = Payment.objects.get(payment_id=payment_id)
            payment.direction = info['direction']
            payment.city = info['city']
            payment.cellphone = info['cellphone']
            payment.save()

    else:
        form_payment_khipu = KhipuCreatePaymentForm(**{'payment_id': payment_id})


    return render(request, 'khipu.html', {'form_payment_khipu': form_payment_khipu, 'payment_id': payment_id})

def shipping_data(request):

    print(Payment.objects.get(payment_id='xgmzvlsfu4sm').direction)

    if 'shipping_data' in request.session:
        info = request.session['shipping_data']
    else:
        info = {"direction": "", "city": "", "cellphone": ""}

    if request.method == "POST" and request.POST.get("save"):

        direction = request.POST.get("direction")
        city = request.POST.get("city")
        cellphone = request.POST.get("cellphone")

        if direction and city and cellphone:
            info = {"direction": direction, "city": city, "cellphone": cellphone}

            # guardamos la información en session variables para obtenerlas en otra vista
            request.session['shipping_data'] = info

            return redirect('/cart/khipuAPI/')

    return render(request, 'shipping_data.html', {"info": info})