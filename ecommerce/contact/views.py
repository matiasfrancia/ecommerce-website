from django.shortcuts import render
from django.core.mail import send_mail
from .forms import EmailForm

# Create your views here.

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


