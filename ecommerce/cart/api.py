# Funcionalidades del carrito

# comprueba si la cantidad es válida y retorna la versión corregida
def to_valid_quantity(quantity):

    quantity = abs(int(quantity))

    if quantity == 0:
        quantity = 1

    return quantity

# agregar elemento al carrito (crea uno nuevo si no exite ya)
def new_element(request, id, quantity):

    quantity = to_valid_quantity(quantity)

    if 'cart' not in request.session:
        request.session['cart'] = [[id, quantity]]
    else:
        new_cart = request.session['cart']
        new_cart.append([id, quantity])
        request.session['cart'] = new_cart

# eliminar elemento del carrito
def delete_element(request, id):

    if 'cart' in request.session:
        request.session['cart'] = list(filter(lambda x: x[0] != id, request.session['cart']))

# actualizar el carrito
def find_element(request, id):

    if 'cart' in request.session:
        for i in range(len(request.session['cart'])):
            if request.session['cart'][i][0] == id:
                return i

    return None

# asigna un valor a la cantidad del elemento
def set_quantity(request, id, quantity):

    quantity = to_valid_quantity(quantity)

    index = find_element(request, id)

    if index != None:
        new_cart = request.session['cart']
        new_cart[index][1] = quantity
        request.session['cart'] = new_cart
    else:
        new_element(request, id, quantity)

# añadir una cierta cantidad del elemento al carrito (puede ser negativo)
def add_quantity(request, id, quantity):

    index = find_element(request, id)

    if index != None:
        if quantity + request.session['cart'][index][1] <= 0: return
        print("Cantidad actual: ", request.session['cart'][index][1])
        # para actualizar el carro se debe reasignar la variable de sesión
        new_cart = request.session['cart']
        new_cart[index][1] += quantity
        request.session['cart'] = new_cart
    else:
        new_element(request, id, quantity)

# obtener todos los elementos del carrito
def get_cart(request):

    if 'cart' in request.session:
        return request.session['cart']

    return None

# eliminar el carrito
def delete_cart(request):

    if 'cart' in request.session:
        del request.session['cart']

# TODO: crear función que convierta un modelo con la información del carro en un carro en las variables
# de sesión, de modo que se guarde la información del carro cuando se sale de la sesión y se vuelve a entrar