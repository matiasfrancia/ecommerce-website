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

from .models import Product, Category
from .forms import ProductModelForm
# Create your views here.

# Falta validar el formulario

def product_search(request):

    try:
        search_data = request.GET.get('search')
        print(search_data)
    except:
        search_data = None
    
    if search_data:
        products = Product.objects.filter(title__icontains=search_data)
        context = {"products": products, "search_data": search_data}
    else:
        context = {}

    return render(request, "product_search.html", context)

def product_inventory(request, id):

    print(request.POST)
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
                    
    return render(request, "product_inventory.html", 
        {"p": product, "movement_list": movement_list, "error": error})

def product_categories(request, id):

    product = Product.objects.get(id=id)

    if request.method == 'POST':

        newCateg = request.POST.get('newCateg')
        delCateg = request.POST.get('delCateg')
        newName = request.POST.get('newName')
        newValue = request.POST.get('newValue')

        if newCateg and newName and newValue:
            product.category_set.create(name = newName, value = newValue)

        if delCateg:
            for elem in request.POST:
                if 'category' in elem:
                    id_del = int(elem.replace('category', ''))
                    categ_del = product.category_set.get(id=id_del)
                    categ_del.delete()

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

    # si el stock de un producto es 0, se debe desactivar
    for product in products:
        if product.stock <= 0:
            product.stock_active = False
        else:
            product.stock_active = True
        product.save()

    context = {"products": products}

    return render(request, "product_list.html", context)

class ProductDetailView(DetailView):
    template_name = "product_detail.html"
    queryset = Product.objects.all()

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

class ProductUpdateView(UpdateView):
    template_name = "product_update.html"
    form_class = ProductModelForm
    queryset = Product.objects.all()

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

    def form_valid(self, form):
        print(form.cleaned_data)
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