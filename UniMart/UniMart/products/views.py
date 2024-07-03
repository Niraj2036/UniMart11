# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductMaster
from users.models import User
from django.contrib import messages
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings

s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name=settings.AWS_REGION_NAME)

BUCKET_NAME = settings.AWS_S3_BUCKET_NAME

def list_products(request):
    email = request.session.get('user_email')
    seller =User.objects.get(email=email)
    products = Product.objects.filter(seller=seller)
    if not products:
        messages.info(request, 'You have no products.')
    return render(request, 'products/list_products.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        email = request.session.get('user_email')
        seller =User.objects.get(email=email)
        photo = request.FILES.get('photo')

        product_master = ProductMaster.objects.filter(product_name=product_name).first()

        

        if photo:
            try:
                s3.upload_fileobj(photo, BUCKET_NAME, photo.name)
                photo_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{photo.name}'
            except NoCredentialsError:
                messages.error(request, 'AWS credentials not available.')
                return redirect('add_product')

        if not product_master:
            ProductMaster.objects.create(
                product_name=product_name,
                description=description,
                unit=unit,
                photo_url=photo_url
            )
        Product.objects.create(
            product_name=product_master,
            description=description,
            photo_url=photo_url,
            price=price,
            unit=unit,
            seller=seller
        )
        
        return redirect('list_products')

    return render(request, 'products/add_product.html')

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.unit = request.POST.get('unit')
        photo = request.FILES.get('photo')

        if photo:
            try:
                s3.upload_fileobj(photo, BUCKET_NAME, photo.name)
                photo_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{photo.name}'
                product.photo_url = photo_url
            except NoCredentialsError:
                messages.error(request, 'AWS credentials not available.')
                return redirect('edit_product', product_id=product.id)

        product.save()
        return redirect('list_products')

    return render(request, 'products/edit_product.html', {'product': product})

# def delete_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     name=product.product_name
#     product.delete()
#     product=Product.objects.filter(product_name=name).first()
#     if not product:
        
#     return redirect('')
