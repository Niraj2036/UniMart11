from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('seller', 'Seller'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    photo_url = models.URLField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
