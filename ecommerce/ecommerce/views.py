from django.shortcuts import render, redirect
from products.models import Product
from .forms import EmailForm

def home(request):

    products = Product.objects.all()

    return render(request, "index.html", {"ps": products})


def contact(request):

    form = EmailForm(request.POST or None)

    if request.method == "POST":
        
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            
            print(subject,message,email)
            send_mail(
                subject,
                message+"\nFrom: "+email,
                '',
                [''], #Correo de la empresa
                fail_silently=False,
            )

    return render(request, "contact.html", {"form": form})

def about_us(request):

    return render(request, "about_us.html", {})