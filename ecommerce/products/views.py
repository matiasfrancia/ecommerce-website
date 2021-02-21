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

class ProductListView(ListView):
    template_name = "product_list.html"
    queryset = Product.objects.all()

class ProductDetailView(DetailView):
    template_name = "product_detail.html"
    queryset = Product.objects.all()

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

class ProductUpdateView(UpdateView):
    template_name = "product_create.html"
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