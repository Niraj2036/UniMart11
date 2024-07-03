from django.urls import path
from . import views
urlpatterns=[
    path("register/",views.registerShop,name="registerShop"),
    path("seller-profile/",views.seller_profile,name="seller_profile"),
    path('update_personal_info/', views.update_personal_info, name='update_personal_info'),
    path('update_shop_info/', views.update_shop_info, name='update_shop_info'),
    path('update_user_photo/', views.update_user_photo, name='update_user_photo'),
    path('update_shop_logo/', views.update_shop_logo, name='update_shop_logo'),
]