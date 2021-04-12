from django.shortcuts import render, redirect, HttpResponse
from products.models import Product, CategoryFilter
from khipu.models import Payment
from khipu.views import get_payment_by_id, refound
from django.db.models import Q
import datetime
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from cart import api as cart_api
# Create your views here.

# No está funcionando negative_stocks
# El inventario se actualiza únicamente cuando se ingresa al carro de compras

# página a la cual redireccionaremos al usuario luego de haber completado el pago
def payment_detail(request):

    # si está el id en las cookies
    payment_id = get_payment_id(request)

    if payment_id == None: return redirect("/404/")

    payment = Payment.objects.get(payment_id=payment_id)
    
    payment_status_update_by_id(request, payment_id, payment)
    if payment.status != "done": return HttpResponse("El pago aún está siendo verificado. Intente en unos segundos.")

    pay_dict = create_payment_template(request, payment)

    context = {"payment": pay_dict}
    
    return render(request, "payment_detail.html", context)

def payments(request):
    return render(request, "payments.html")

# actualiza un pago en función de su ID
def payment_status_update_by_id(request, id, payment=None):

    if not payment:
        payment = Payment.objects.get(payment_id=id)
    
    # conexión con khipu: actualiza el estado del pago en la base de datos
    get_payment_by_id(id)

    if payment.status == 'done':

        delete_payment_id(request)

        if 'shipping_data' in request.session:
            del request.session['shipping_data']

        cart_api.delete_cart(request)

        # descontar del stock las nuevas compras realizadas
        enter_movements_payment('salida', payment)
    
# Actualizamos el estado de las compras que no están terminadas (en la db)
def payments_status_update(request, payments):

    for payment in payments:
        id = payment.payment_id
        
        payment_status_update_by_id(request, id, payment)

# Si ya expiró el pago (y aún no está pagado) entonces lo elimina de la base de datos
def payment_expired_delete(payments):

    for i in range(len(payments)-1, -1, -1):
        if pending_payment_expired(payments[i]):
            payments[i].delete()

def create_payment_template(request, payment):
    
    custom = json.loads(payment.custom)
    cart_products = custom['cart_products']
    negative_stocks = json.loads(payment.negative_stocks)

    # formateamos la información para pasársela al template
    pay_dict = {
        'negative_stocks': negative_stocks, # puede ser [] si no hubo problemas de stock
        'cart_products': cart_products,
        'amount': int(payment.amount[:-5]),
        'payment_id': payment.payment_id,
        'payer_email': payment.payer_email,
        'payer_name': payment.payer_name,
    }

    return pay_dict

# Crea una lista de pagos con toda la información que se usará en el template
def create_payments_for_template(request, payments):

    payments_info = []

    for payment in payments:
        
        pay_dict = create_payment_template(request, payment)

        payments_info.append(pay_dict)

    return payments_info

# Actualiza los pagos y crea una lista con la información de cada pago para pasársela al template
def payment_data(request):

    payments_update = Payment.objects.exclude(status = 'done')

    payments_status_update(request, payments_update)
    payment_expired_delete(payments_update)

    # Guardamos en una lista los pagos a imprimir en pantalla
            
    payments = Payment.objects.filter(status = 'done')
    payments = payments.order_by('-conciliation_date')

    # Parsea el detalle de compra desde la base de datos

    payments_info = create_payments_for_template(request, payments)
    
    return JsonResponse(payments_info, safe=False)

# función que retorna true si el pago debe ser eliminado, false en caso contrario
def pending_payment_expired(payment):
    if payment.status == 'pending':
        expires = payment.expires_date
        now = datetime.datetime.today()

        expires_date = datetime.datetime(expires.year, expires.month, expires.day, expires.hour, expires.minute, expires.second)
        now_date = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

        if expires_date < now_date:
            return True
    return False

def refound_view(request, id):

    if request.method == "POST":
        refounded = False
        try:
            refound(id)
            refounded = True
        except:
            print("El reembolso no pudo ser realizado")
        
        if refounded:
            payment = Payment.objects.get(payment_id=id)

            enter_movements_payment('reembolso', payment)
            payment.delete()

            return redirect(reverse('payment:payments'))

    return render(request, "refound.html",{"id":id})


# ingresa los movimientos correspondientes a un carro de compras (puede ser entrada o salida)
# retorna una lista con los productos que quedaron con stock negativo
def enter_movements_payment(movement_type, payment):

    print("Entro a la función enter_movements_payment")

    try:
        products = Product.objects.all()

        custom = json.loads(payment.custom)
        cart_products = custom['cart_products']
        date_movement = datetime.date.today()

        negative_stocks = {}

        for item in cart_products:

            product = products.get(id=item['product_id'])
            delta_quantity = item['product_quantity']

            # si el stock queda negativo se puede solucionar reembolsando el dinero o agregando otra entrada del producto
            if movement_type == 'salida':
                
                if product.stock - delta_quantity < 0:
                    negative_stocks[str(product.id)] =  product.stock - delta_quantity

                product.stock -= delta_quantity
                print("Product.stock = ", product.stock)
                product.movement_set.create(mov_data = movement_type, date = date_movement, quantity = delta_quantity)
                product.save()

            elif movement_type == 'entrada' or movement_type == 'reembolso':
                product.stock += delta_quantity
                product.movement_set.create(mov_data = movement_type, date = date_movement, quantity = delta_quantity)
                product.save()

        payment.negative_stocks = json.dumps(negative_stocks)
        payment.save()

    except:
        print("Algo falló en la función enter_movements_payment")

# guarda la información del despacho en las variables de sesión (la valida) y redirige a la página del pago
def shipping_data(request):

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

# guarda la id del pago en las variables de sesión
def save_payment_id(request, payment_id):

    if payment_id == '' or payment_id == None:
        print("Se trató de guardar una id vacía en las variables de sesión (save_payment_id)")
        return

    if 'payment_id' not in request.session:
        request.session['payment_id'] = payment_id

def get_payment_id(request):

    if 'payment_id' in request.session:
        return request.session['payment_id']

    return None

def delete_payment_id(request):

    if 'payment_id' in request.session:
        del request.session['payment_id']