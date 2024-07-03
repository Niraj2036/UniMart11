from django.shortcuts import render, redirect
from users.models import User
from .models import Shop
from django.contrib import messages
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name=settings.AWS_REGION_NAME)

BUCKET_NAME = settings.AWS_S3_BUCKET_NAME


def registerShop(request):
    email = request.session.get('user_email')
    print(email)
    user = User.objects.get(email=email)
    
    if request.method == 'POST':
        shopName = request.POST.get('shop_name')
        addr = request.POST.get('address')
        category = request.POST.get('shopcategory')
        shop_logo = request.FILES.get('shop_logo')

        if shopName.strip() == '':
            messages.error(request, 'Shop name cannot be blank')
        elif addr.strip() == '':
            messages.error(request, 'Shop address cannot be blank')
        elif category is None or category.strip() == '':
            messages.error(request, 'Please select Shop Category')
        elif not shop_logo:
            messages.error(request, 'Shop logo is required.')
        else:
            try:
                s3.upload_fileobj(shop_logo, BUCKET_NAME, shop_logo.name)
                shop_logo_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{shop_logo.name}'
            except NoCredentialsError:
                messages.error(request, 'AWS credentials not available.')
                return render(request, 'shops/create_shop.html', {'messages': messages.get_messages(request)})

            shop = Shop.objects.create(
                name = shopName,
                address = addr,
                category = category,
                logo_url = shop_logo_url,
                seller = user,
            )
            messages.success(request, 'Shop Registered successfully')
    
    return render(request, 'shops/create_shop.html',user = User.objects.get(email=user_email),shop = Shop.objects.get(seller=user))

def seller_profile(request):
    user_email = request.session.get('user_email')
    user = User.objects.get(email=user_email)
    shop = Shop.objects.get(seller=user)
    return render(request, 'shops/seller_profile.html', {'user': user, 'shop': shop})

def update_personal_info(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        if not user_email:
            messages.error(request, 'User email not found in session.')
            return redirect('../seller-profile/')  # Replace with appropriate redirect

        name = request.POST.get('name')
        mobile_no = request.POST.get('mobile')

        try:
            user = User.objects.get(email=user_email)
            user.name = name
            user.mobile_no = mobile_no
            user.save()
            messages.success(request, 'Personal information updated successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except Exception as e:
            messages.error(request, f'Failed to update personal information: {str(e)}')

    return redirect('../seller-profile/')  # Replace with appropriate redirect

def update_shop_info(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        if not user_email:
            messages.error(request, 'User email not found in session.')
            return redirect('../seller-profile/')  # Replace with appropriate redirect

        shop_name = request.POST.get('shop-name')
        address = request.POST.get('address')
        category = request.POST.get('category')

        try:
            user = User.objects.get(email=user_email)
            shop = user.shops.first()  # Assuming a user can have only one shop
            if shop:
                shop.name = shop_name
                shop.address = address
                shop.category = category
                shop.save()
                messages.success(request, 'Shop information updated successfully.')
            else:
                messages.error(request, 'Shop does not exist for the user.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except Exception as e:
            messages.error(request, f'Failed to update shop information: {str(e)}')

    return redirect('../seller-profile/')  # Replace with appropriate redirect

def update_user_photo(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        if not user_email:
            messages.error(request, 'User email not found in session.')
            return redirect('../seller-profile/')  # Replace with appropriate redirect

        profile_photo = request.FILES.get('profile_photo')

        try:
            user = User.objects.get(email=user_email)

            if not profile_photo:
                messages.error(request, 'No file selected.')
            else:
                # Upload photo to S3
                s3.upload_fileobj(profile_photo, BUCKET_NAME, profile_photo.name)
                user.photo_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{profile_photo.name}'
                user.save()
                messages.success(request, 'Profile photo updated successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except Exception as e:
            messages.error(request, f'Failed to update profile photo: {str(e)}')

    return redirect('../seller-profile/')  # Replace with appropriate redirect

def update_shop_logo(request):
    if request.method == 'POST':
        user_email = request.session.get('user_email')
        if not user_email:
            messages.error(request, 'User email not found in session.')
            return redirect('../seller-profile/')  # Replace with appropriate redirect

        shop_logo = request.FILES.get('shop_logo')

        try:
            user = User.objects.get(email=user_email)
            shop = user.shops.first()  # Assuming a user can have only one shop

            if not shop:
                messages.error(request, 'Shop does not exist for the user.')
            elif not shop_logo:
                messages.error(request, 'No file selected.')
            else:
                # Upload logo to S3
                s3.upload_fileobj(shop_logo, BUCKET_NAME, shop_logo.name)
                shop.logo_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{shop_logo.name}'
                shop.save()
                messages.success(request, 'Shop logo updated successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except Exception as e:
            messages.error(request, f'Failed to update shop logo: {str(e)}')

    return redirect('../seller-profile/')  # Replace with appropriate redirect