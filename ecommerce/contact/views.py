from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.

def contact(request):

    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        email = request.POST.get('email')
        
        if email and message:
            print(subject,message,email)
            send_mail(
                subject,
                message,
                email,
                [''],
                fail_silently=False,
            )


    return render(request, "contact.html")


