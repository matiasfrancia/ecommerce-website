from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, 
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    View,
)

from .models import Product
from .forms import ProductModelForm

# Create your views here.

class ProductCreateView(CreateView):
    template_name = "product_create.html"
    form_class = ProductModelForm
    queryset = Product.objects.all()

    def form_valid(self, form):
        return super().form_valid(form)

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

class ProductDeleteView(DeleteView):
    template_name = "product_delete.html"

    def get_object(self):
        idToCreate = self.kwargs.get("id")
        return get_object_or_404(Product, id=idToCreate)

    def get_success_url(self):
        return reverse("products:product-list")