from django.shortcuts import render, redirect
from .forms import RegisterForm
from products.models import Product
from khipu.models import Payment
from khipu.views import get_payment_by_id
from django.db.models import Q
import datetime

# Create your views here.
def register(request):

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()

        return redirect('/home/')

    context = {"form": form}

    return render(request, "register/register.html", context)

def profile(request):

    products = Product.objects.all()

    context = {"products": products}

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

    """ for payment in payments_update:
        print("ID: ", payment.payment_id, ", Fecha de expiración: ", payment.expires_date) """

    # Guardamos en una lista los pagos a imprimir en pantalla
            
    payments = Payment.objects.filter(status = 'done')
    payments = payments.order_by('-conciliation_date')

    # Parsea el detalle de compra desde la base de datos

    payments_parsed = []

    for payment in payments:
        
        custom = payment.custom.split('&&')
        pq_parsed = product_quantity_parser(custom)
        if pq_parsed == [('', '')]:
            pq_parsed = []

        pay_dict = {
            'pq_list': pq_parsed,
            'amount': int(payment.amount[:-5]),
            'payment_id': payment.payment_id,
            'payer_email': payment.payer_email,
            'payer_name': payment.payer_name,
        }

        payments_parsed.append(pay_dict)

    context = {'payments': payments_parsed}

    return render(request, "payments.html", context)

# return [(product, quantity), ...]
def product_quantity_parser(list):
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
    return parsed_list

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