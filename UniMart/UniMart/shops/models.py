from django.db import models
from users.models import User  # Assuming your User model is defined in models.py

class Shop(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=512)
    category = models.CharField(max_length=100)
    logo_url = models.URLField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')

    def __str__(self):
        return self.name
