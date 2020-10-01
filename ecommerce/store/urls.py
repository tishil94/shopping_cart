from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name = "store"),
    path('cart/', views.cart, name = "cart"),
    path('checkout/', views.checkout, name = "checkout"),
    path('login/', views.login, name = "login"),
    path('register/', views.register, name = "register"),
    path('logout/', views.logout, name = "logout"),
    path('product/<str:pk>/', views.product, name="product"),
    path('otp/', views.otp, name = "otp"),
    path('mobile/', views.mobile, name = "mobile"),
    path('orders/', views.orders, name = "orders"),
    
  
    path('update_item/', views.updateItem, name = "update_item"),
    path('process_order/', views.processOrder, name = "process_order"),

    path('admin_login/', views.admin_login, name = "admin_login")


]