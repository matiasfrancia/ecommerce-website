from django.shortcuts import render, redirect
from .forms import RegisterForm
from products.models import Product

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