from django.urls import path
from django.contrib import admin
from .views import (ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView)
from . import views

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name = 'product-list'),
    path('<int:id>/', ProductDetailView.as_view(), name = 'product-detail'),
    path('create/', ProductCreateView.as_view(), name = 'product-create'),
    path('<int:id>/update/', ProductUpdateView.as_view(), name = 'product-update'),
    path('<int:id>/delete/', ProductDeleteView.as_view(), name = 'product-delete'),
    path('<int:id>/categories/', views.product_categories, name = 'product-categories'),
    path('<int:id>/inventory/', views.product_inventory, name = 'product-inventory'),
]