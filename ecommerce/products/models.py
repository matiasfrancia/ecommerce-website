from django.db import models
from django.urls import reverse

class Category(models.Model):
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    tag = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length = 120)
    description = models.TextField()
    image = models.FileField(upload_to="products/images/")
    price = models.IntegerField()
    active = models.BooleanField(default = True)
    category = models.ForeignKey(Category, default=None, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args,**kwargs)

