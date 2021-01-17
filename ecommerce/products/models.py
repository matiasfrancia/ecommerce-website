from django.db import models
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length = 120)
    description = models.TextField()
    image = models.FileField(upload_to="products/images/")
    price = models.IntegerField()
    active = models.BooleanField(default = True)

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})