from django.db import models
from django.urls import reverse
import datetime

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length = 120)
    description = models.TextField()
    image = models.FileField(upload_to="products/images/")
    price = models.IntegerField()
    active = models.BooleanField(default = True)
    stock = models.IntegerField(default = 0)
    stock_active = models.BooleanField(default = False)

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args,**kwargs)

    def __str__(self):
        return self.title

class Category(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Movement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    mov_data = models.CharField(
        "Movimiento",
        max_length = 50,
        choices = [('entrada', 'Entrada de producto'), ('salida', 'Salida de producto')],
        null = True,
        blank = True
    )
    date = models.DateField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.mov_data + ": " + str(self.date)