from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Address
from shops.models import Shop
import hashlib
from django.http import HttpResponseRedirect, HttpResponse
import re
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
def register(request):
    if request.method == 'POST':
        name = request.POST.get('user_name')
        phone = request.POST.get('mobile_no')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password = request.POST.get('pass')
        confirm_pass = request.POST.get('cnfpass')
        role = 'seller' if 'registerAsSeller' in request.POST else 'user'
        photo_url = 'https://unimart12.s3.eu-north-1.amazonaws.com/blank-profile-picture-973460_960_720-1.png'
        
        request_data = {
            'user_name': name,
            'mobile_no': phone,
            'email': email,
            'address': address,
            'registerAsSeller': 'registerAsSeller' in request.POST
        }
        
        # Check if all fields are filled or not
        if name.strip() == '':
            messages.error(request, 'Name cannot be blank')
        elif phone.strip() == '':
            messages.error(request, 'Phone No. cannot be blank')
        elif len(phone) != 10:
            messages.error(request, 'Please enter a valid Phone No.')
        elif not phone.isdigit():
            messages.error(request, 'Please enter a valid Phone No.')
        elif email.strip() == '':
            messages.error(request, 'Email cannot be blank')
        elif address.strip() == '':
            messages.error(request, 'Address cannot be blank')
        elif password.strip() == '':
            messages.error(request, 'Password cannot be blank')
        elif password != confirm_pass:
            messages.error(request, 'Passwords do not match')
        elif len(password) < 4:
            messages.error(request, 'Password should have at least 4 characters')
        elif not re.search(r'[A-Z]', password):
            messages.error(request, 'Password should have at least one Uppercase letter')
        elif not re.search(r'[a-z]', password):
            messages.error(request, 'Password should contain at least one lowercase letter')
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists, please Login')
            else:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user = User.objects.create(
                    name=name,
                    email=email,
                    photo_url=photo_url,
                    mobile_no=phone,
                    password=hashed_password,
                    role=role,
                )
                Address.objects.create(
                    user=user,
                    address=address,
                )
                messages.success(request, 'Registration successful. Please log in.')
                return HttpResponseRedirect("../login/")

        return render(request, 'register.html', {'request_data': request_data})
    return render(request,'users/register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email is None or email.strip() == '':
            messages.error(request, 'Email cannot be blank')
        elif password is None or password.strip() == '':
            messages.error(request,'Password cannot be blank')
        else:
            try:
                user=User.objects.get(email=email)
                hashed_password= hashlib.sha256(password.encode()).hexdigest()

                if user.password == hashed_password:
                    request.session['user_email']=user.email
                    messages.success(request,'Logged in Successfully')
                    if user.role == 'seller':
                        if Shop.objects.filter(seller=user).exists():
                            return HttpResponseRedirect('../../shop/seller-profile/')
                        else:
                            return HttpResponseRedirect("../../shop/register/")
                else:
                    messages.error(request,'Invalid credentials. Please try again.')
            except User.DoesNotExist:
                messages.error(request,"User doesn't exist please login")

    return render(request,'users/login.html')

def generate_otp():
    return str(secrets.randbelow(999999)).zfill(6)

def send_otp_email(email, otp):
    sender_email = settings.EMAIL_HOST_USER
    receiver_email = email
    password = settings.EMAIL_HOST_PASSWORD

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Your OTP for Password Reset'

    body = f'Your OTP for password reset is: {otp}'
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("OTP Email sent successfully")
    except Exception as e:
        print(f"Error sending OTP email: {e}")
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            send_otp_email(email, otp)
            request.session['otp'] = otp
            request.session['reset_email'] = email
            return redirect('../verify_otp/')
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    return render(request, 'users/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = ''.join([
            request.POST.get('otp_digit_0', ''),
            request.POST.get('otp_digit_1', ''),
            request.POST.get('otp_digit_2', ''),
            request.POST.get('otp_digit_3', ''),
            request.POST.get('otp_digit_4', ''),
            request.POST.get('otp_digit_5', '')
        ])
        print(entered_otp)
        saved_otp = request.session.get('otp')
        print(saved_otp)
        if entered_otp == saved_otp:
            messages.success(request, "OTP verification successful.")
            return HttpResponseRedirect("../reset_password/")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'users/verify_otp.html', {'otp_range': range(6)})

def reset_password(request):
    email=request.session.get('reset_email')
    if request.method=='POST':
        password=request.POST.get('password')
        print(password)
        cnf_pass=request.POST.get('cnf_password')
        print(cnf_pass)
        if password.strip() == '':
            messages.error(request, 'Password cannot be blank')
        elif password != cnf_pass:
            messages.error(request, 'Passwords do not match')
        elif len(password) < 4:
            messages.error(request, 'Password should have at least 4 characters')
        elif not re.search(r'[A-Z]', password):
            messages.error(request, 'Password should have at least one Uppercase letter')
        elif not re.search(r'[a-z]', password):
            messages.error(request, 'Password should contain at least one lowercase letter')
        else:
            user=User.objects.get(email=email)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user.password=hashed_password
            messages.success(request, 'Password reset successful')
            return HttpResponseRedirect("../login/")
    return render(request,'users/reset_password.html')

def resend_otp(request):
    email = request.session.get('reset_email')
    if email:
        otp = generate_otp()  # Generate a new OTP
        request.session['otp'] = otp  # Store the new OTP in session
        send_otp_email(email, otp)  # Send the OTP to the user's email
        messages.success(request, "OTP has been resent successfully.")  # Success message
    else:
        messages.error(request, "Email not found in session. Please initiate the reset process again.")  # Error message
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




            

        
