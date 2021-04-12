"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from . import views
from register import views as register_views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path("home/", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("aboutus/", views.about_us, name="about-us"),
    path("cart/", include('cart.urls')),
    path('payments/', include('payment.urls')),
    path("register/", register_views.register, name="register"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", register_views.profile, name="profile"),
    re_path(r'^khipu/', include('khipu.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()