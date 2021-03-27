from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView, 
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    View,
)

from .models import Product, Category, CategoryFilter, History
from .forms import ProductModelForm
import datetime

# Create your views here.

# Falta validar el formulario

def delete_category_filter(request, id):

    category = CategoryFilter.objects.get(id=id)

    if request.method == "POST":
        if request.POST.get('delete'):
            category.delete()
            return redirect("/products/categories/")

    return render(request, "delete_category_filter.html", {"category": category})

def rename_category_filter(request, id):

    category = CategoryFilter.objects.get(id=id)

    if request.method == "POST":
        
        if request.POST.get('save'):
            category.name = request.POST.get('newName')
            category.save()
            return redirect("/products/categories/")

    return render(request, "rename_category_filter.html", {"category": category})

def category_filters(request):

    #TODO: permitir que sólo se pueda seleccionar una categoría para modificar y/o eliminar

    categories = CategoryFilter.objects.all()
    categ_rename = None

    if request.method == 'POST':

        newCateg = request.POST.get('newCateg')
        delCateg = request.POST.get('delCateg')
        renameCateg = request.POST.get('renameCateg')
        newName = request.POST.get('newName')
        newValue = request.POST.get('newValue')

        print(request.POST)

        if newCateg and newName:
            categories.create(name = newName)

        if delCateg:
            for elem in request.POST:
                if 'category_filter' in elem:
                    #TODO: crear función para eliminar elementos de la base de datos
                    id_del = int(elem.replace('category_filter', ''))
                    return redirect('/products/categories/%i/delete/' % id_del)

        if renameCateg:
            for elem in request.POST:
                if 'category_filter' in elem:
                    id_rename = int(elem.replace('category_filter', ''))
                    categ_rename = categories.get(id=id_rename)
                    return redirect('/products/categories/%i/rename/' % id_rename)

    context = {"categories": categories, "categ_rename": categ_rename}

    return render(request, "category_filters.html", context)

def product_search(request):

    try:
        search_data = request.GET.get('search')
    except:
        search_data = None
    
    if search_data:
        products = Product.objects.filter(title__icontains=search_data)
        context = {"products": products, "search_data": search_data}

        # si la cantidad de productos en la lista es 1 manda una señal al template
        if len(products) <= 2:
            context["one_product"] = True
    else:
        context = {}

    return render(request, "product_search.html", context)

def product_inventory(request, id):

    product = Product.objects.get(id=id)

    error = """"""

    if request.method == 'POST':

        newMovement = request.POST.get('newMovement')
        delMovement = request.POST.get('delMovement')
        newMovData = request.POST.get('newMovData')
        newDate = request.POST.get('newDate')
        newQuantity = request.POST.get('newQuantity')

        if newMovement and newMovData and newDate and newQuantity:
            
            delta_quantity = abs(int(newQuantity))

            # sumamos la cantidad de stock del producto
            if newMovData == 'entrada':
                product.stock += delta_quantity
                product.movement_set.create(mov_data = newMovData, date = newDate, quantity = delta_quantity)
                product.save()
                return redirect("/products/%i/inventory/" % id)

            else:

                if product.stock - delta_quantity >= 0:
                    product.stock -= delta_quantity
                    product.movement_set.create(mov_data = newMovData, date = newDate, quantity = delta_quantity)
                    product.save()
                    return redirect("/products/%i/inventory/" % id)

                else:
                    error = """Si agrega esta salida, el stock total del producto será negativo. 
                                Procure que siempre sea positivo o 0."""

                    movement_list = product.movement_set.order_by('date')

                    return render(request, "product_inventory.html", 
                        {"p": product, "movement_list": movement_list, "error": error})

        if delMovement:

            for elem in request.POST:

                if 'movement_id' in elem:
                    id_del = int(elem.replace('movement_id', ''))
                    move_del = product.movement_set.get(id=id_del)
                    if move_del.mov_data == "entrada":
                        if product.stock - move_del.quantity >= 0:
                            product.stock -= move_del.quantity
                            move_del.delete()
                        else:
                            error = """Si elimina este movimiento, el stock total del producto será negativo. 
                                        Procure que siempre sea positivo o 0."""
                    else:
                        product.stock += move_del.quantity
                        move_del.delete()

                    product.save()

    movement_list = product.movement_set.order_by('date')

    date = datetime.date.today()
                    
    return render(request, "product_inventory.html", 
        {"p": product, "movement_list": movement_list, "error": error, "date": date})

def product_categories(request, id):

    product = Product.objects.get(id=id)

    if request.method == 'POST':

        newCateg = request.POST.get('newCateg')
        delCateg = request.POST.get('delCateg')
        newName = request.POST.get('newName')
        newValue = request.POST.get('newValue')

        if newCateg and newName and newValue:
            product.category_set.create(name = newName, value = newValue)
            return redirect('/products/%i/categories' %id)

        if delCateg:
            for elem in request.POST:
                if 'category' in elem:
                    id_del = int(elem.replace('category', ''))
                    categ_del = product.category_set.get(id=id_del)
                    categ_del.delete()
            return redirect('/products/%i/categories' %id)

        if request.POST.get('save'):
            return redirect("/products/%i" %id)
                    
    return render(request, "product_categories.html", {"p": product})

class ProductCreateView(CreateView):
    template_name = "product_create.html"
    form_class = ProductModelForm
    queryset = Product.objects.all()

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('products:product-categories', kwargs={'id': self.object.pk})

def product_list(request):

    products = Product.objects.all()
    selected = "default"

    # si el stock de un producto es 0, se debe desactivar
    for product in products:
        if product.stock <= 0:
            product.stock_active = False
        else:
            product.stock_active = True
        product.save()
    
    # filtramos los productos a través de su categoría
    categories = CategoryFilter.objects.all()
    
    if request.method == "POST":
        categ_name = request.POST.get('categories')
        selected = categ_name
        
        if categ_name != 'default':
            for categ in categories:
                if categ.name == categ_name:
                    products = categ.product_set.all()

    context = {"products": products, "categories": categories, "selected": selected}

    # si la cantidad de productos en la lista es 1 manda una señal al template
    if len(products) <= 2:
        one_product = True
        context["one_product"] = one_product

    return render(request, "product_list.html", context)

class ProductDetailView(DetailView):
    template_name = "product_detail.html"
    queryset = Product.objects.all()

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

def product_update(request, id):

    instance = get_object_or_404(Product, id=id)

    form = ProductModelForm(request.POST or None, instance=instance)

    product_price = instance.price

    if form.is_valid():
        product = form.save()
        
        # si el precio al actualizar cambia creamos una instancia de ProductHistory
        if product.price != product_price:
            product.history_set.create(price = product.price, date = datetime.date.today())
            print(product.history_set.all())

        return redirect("/profile/")

    context = {"form": form}

    return render(request, "product_update.html", context)

class ProductUpdateView(UpdateView):
    template_name = "product_update.html"
    form_class = ProductModelForm
    queryset = Product.objects.all()

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('products:product-categories', kwargs={'id': self.object.pk})

class ProductDeleteView(DeleteView):
    template_name = "product_delete.html"

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

    def get_success_url(self):
        return reverse("profile")