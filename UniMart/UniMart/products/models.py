from django.db import models
from users.models import User

class ProductMaster(models.Model):
    product_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.product_name

class Product(models.Model):
    product_name = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    seller = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # Allow nulls temporarily

    def __str__(self):
        return self.product_name
