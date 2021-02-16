from django.db import models
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length = 120)
    description = models.TextField()
    image = models.FileField(upload_to="products/images/")
    price = models.IntegerField()
    active = models.BooleanField(default = True)
    price_clp = models.CharField(default='', max_length=50)

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