from django.shortcuts import render, redirect
from .forms import RegisterForm
from products.models import Product
from khipu.models import Payment
from khipu.views import get_payment_by_id, refound
from django.db.models import Q
import datetime
import json
from django.urls import reverse

# Create your views here.
def register(request):

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()

        return redirect('/home/')

    context = {"form": form}

    return render(request, "register/register.html", context)

# Integrar la api de algún servicio de envío

def profile(request):

    products = Product.objects.all()

    context = {}

    if request.user.is_superuser:
        # si el stock de un producto es 0, se debe desactivar
        for product in products:
            if product.stock == 0:
                product.stock_active = False
            else:
                product.stock_active = True
            product.save()

        context = {"products": products}
    
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

        context = {"products": products, "payments": payments_parsed}

    return render(request, "profile.html", context)

def payments(request):

    # Actualizamos el estado de las compras que no están terminadas (en la db)

    payments_update = Payment.objects.exclude(status = 'done')

    for payment in payments_update:
        id = payment.payment_id
        get_payment_by_id(id)

    # Si ya expiró el pago (y aún no está pagado) entonces lo elimina de la base de datos

    for i in range(len(payments_update)-1, -1, -1):
        if delete_pending_payment(payments_update[i]):
            payments_update[i].delete()

    # Guardamos en una lista los pagos a imprimir en pantalla
            
    payments = Payment.objects.filter(status = 'done')
    payments = payments.order_by('-conciliation_date')

    # Parsea el detalle de compra desde la base de datos

    payments_parsed = []

    # obtenemos la lista de productos
    products = Product.objects.all()

    for payment in payments:
        
        """ custom = payment.custom.split('&&')
        pq_parsed = product_quantity_parser(custom)
        if pq_parsed == [('', '')]:
            pq_parsed = [] """

        # descontar del stock las nuevas compras realizadas
        custom = json.loads(payment.custom)
        cart_products = custom['cart_products']

        date_movement = datetime.date.today()

        for item in cart_products:

            product = products.get(id=item['product_id'])

            delta_quantity = item['product_quantity']

            if product.stock - delta_quantity >= 0:
                product.stock -= delta_quantity
                product.movement_set.create(mov_data = 'salida', date = date_movement, quantity = delta_quantity)
                product.save()
            else:
                error = """Si agrega esta salida, el stock total del producto será negativo. 
                            Procure que siempre sea positivo o 0."""

        # formateamos la información para pasársela al template
        pay_dict = {
            'cart_products': cart_products,
            'amount': int(payment.amount[:-5]),
            'payment_id': payment.payment_id,
            'payer_email': payment.payer_email,
            'payer_name': payment.payer_name,
        }

        payments_parsed.append(pay_dict)

    context = {'payments': payments_parsed}

    return render(request, "payments.html", context)

# return [(product, quantity), ...]
""" def product_quantity_parser(list):
    parsed_list = []
    for pq in list:
        div_pos = 0
        for i in range(len(pq)-1, -1, -1):
            if pq[i] == ':':
                div_pos = i
                break
        p = pq[:div_pos]
        q = pq[div_pos+1::]
        parsed_list.append((p, q))
    return parsed_list """

# función que retorna true si el pago debe ser eliminado, false en caso contrario
def delete_pending_payment(payment):
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
            payment.delete()
            return redirect(reverse('payments'))

    return render(request, "refound.html",{"id":id}) 