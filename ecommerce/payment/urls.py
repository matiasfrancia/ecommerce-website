from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path("", views.payments, name="payments"),
    path("payments-json/", views.payment_data, name="payments-json"),
    path("detail/", views.payment_detail, name="payment-detail"),
    path("refound/<id>", views.refound_view, name="refound"),
    path("shipping/", views.shipping_data, name="shipping")
]
