from django.urls import path
from . import views
urlpatterns=[
    path("register/",views.register,name='register'),
    path("login/",views.login,name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
]