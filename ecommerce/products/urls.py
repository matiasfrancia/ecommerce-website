from django.urls import path
from django.contrib import admin
from .views import (ProductCreateView)
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name = 'product-list'),
    path('<int:id>/', views.product_detail, name = 'product-detail'),
    path('create/', ProductCreateView.as_view(), name = 'product-create'),
    path('<int:id>/update/', views.product_update, name = 'product-update'),
    path('<int:id>/delete/', views.product_delete, name = 'product-delete'),
    path('<int:id>/categories/', views.product_categories, name = 'product-categories'),
    path('<int:id>/inventory/', views.product_inventory, name = 'product-inventory'),
    path('search/', views.product_search, name = 'product-search'),
    path("categories/", views.category_filters, name="category-filters"),
    path("categories/<int:id>/rename/", views.rename_category_filter, name="rename-category-filters"),
    path("categories/<int:id>/delete/", views.delete_category_filter, name="delete-category-filters"),
]