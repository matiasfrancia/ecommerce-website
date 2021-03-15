from django.shortcuts import render, redirect
from .forms import RegisterForm
from products.models import Product, CategoryFilter
from khipu.models import Payment
from khipu.views import get_payment_by_id, refound
from django.db.models import Q
import datetime
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# Create your views here.
def register(request):

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        new_user = form.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'],
                                )
        login(request, new_user)
        return redirect('/home/')

    context = {"form": form}

    return render(request, "register/register.html", context)

# Integrar la api de algún servicio de envío

def profile(request):

    products = Product.objects.all()
    selected = "default"

    context = {}

    if request.user.is_superuser:
        # si el stock de un producto es 0, se debe desactivar
        for product in products:
            if product.stock == 0:
                product.stock_active = False
            else:
                product.stock_active = True
            product.save()
    
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

        context = {"payments": payments_parsed}

    # filtramos los productos a través de su categoría
    categories = CategoryFilter.objects.all()
    
    if request.method == "POST":
        categ_name = request.POST.get('categories')
        selected = categ_name
        
        if categ_name != 'default':
            for categ in categories:
                if categ.name == categ_name:
                    products = categ.product_set.all()

    # agregamos los productos al context para pasárselos al template
    context["products"] = products
    context["categories"] = categories

    # si la cantidad de productos en la lista es 1 manda una señal al template
    if len(products) <= 2:
        one_product = True
        context["one_product"] = one_product

    return render(request, "profile.html", context)

def payments(request):
    return render(request, "payments.html")

def payment_data(request):
    # Actualizamos el estado de las compras que no están terminadas (en la db)

    payments_update = Payment.objects.exclude(status = 'done')

    for payment in payments_update:
        id = payment.payment_id
        get_payment_by_id(id)

        if payment.status == 'done':

            # descontar del stock las nuevas compras realizadas
            negatives_stocks = enter_movements_payment('salida', payment)
            
            # agregamos negatives_stocks a las variables de sesión si != []
            if negatives_stocks != []:
                request.session[id] = {'negatives_stocks': negatives_stocks}

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
        
        custom = json.loads(payment.custom)
        cart_products = custom['cart_products']

        # obtenemos de las session variables negatives_stocks
        if payment.payment_id in request.session:
            negatives_stocks = request.session[payment.payment_id]['negatives_stocks']
        else:
            negatives_stocks = []

        # formateamos la información para pasársela al template
        pay_dict = {
            'negatives_stocks': negatives_stocks, # puede ser [] si no hubo problemas de stock
            'cart_products': cart_products,
            'amount': int(payment.amount[:-5]),
            'payment_id': payment.payment_id,
            'payer_email': payment.payer_email,
            'payer_name': payment.payer_name,
        }

        payments_parsed.append(pay_dict)
    
    return JsonResponse(payments_parsed, safe=False)

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

            negatives_stocks = enter_movements_payment('entrada', payment)

            # se elimina negatives_stocks de las variables de sesión
            # (también se debería hacer en caso de que se arregle el problema de stock)
            if payment.payment_id in request.session:
                del request.session[payment.payment_id]

            return redirect(reverse('payments'))

    return render(request, "refound.html",{"id":id})


# ingresa los movimientos correspondientes a un carro de compras (puede ser entrada o salida)
# retorna una lista con los productos que quedaron con stock negativo
def enter_movements_payment(movement_type, payment):

    try:
        products = Product.objects.all()

        custom = json.loads(payment.custom)
        cart_products = custom['cart_products']
        date_movement = datetime.date.today()

        negatives_stocks = []

        for item in cart_products:

            product = products.get(id=item['product_id'])
            delta_quantity = item['product_quantity']

            # si el stock queda negativo se puede solucionar reembolsando el dinero o agregando otra entrada del producto
            if movement_type == 'salida':
                
                if product.stock - delta_quantity < 0:
                    negatives_stocks.append("ID - Producto: " + str(product.id) + " - " + product.title + ", Stock final: " + str(product.stock))

                product.stock -= delta_quantity
                product.movement_set.create(mov_data = 'salida', date = date_movement, quantity = delta_quantity)
                product.save()

            elif movement_type == 'entrada':
                product.stock += delta_quantity
                product.movement_set.create(mov_data = 'entrada', date = date_movement, quantity = delta_quantity)
                product.save()

        return negatives_stocks

    except:
        return []