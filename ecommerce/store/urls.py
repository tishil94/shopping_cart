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

    path('admin_login/', views.admin_login, name = "admin_login"),
    path('admin_logout/', views.admin_logout, name = "admin_logout"),

    path('admin_home/', views.admin_home, name = "admin_home"),
    path('product_view/', views.product_view, name = "product_view"),
    path('orders_view/', views.orders_view, name = "orders_view"),
    path('orderitems_view/', views.orderitems_view, name = "orderitems_view"),
    path('shipping_view/', views.shipping_view, name = "shipping_view"),
    path('users_view/', views.users_view, name = "users_view"),
    path('customer_view/', views.customer_view, name = "customer_view"),
    path('add_product/', views.add_product, name = "add_product"),
    path('update_product/<int:id>/', views.update_product, name = "update_product"),
    path('delete_product/<int:id>/', views.delete_product, name = "delete_product"),
    path('update_order/', views.update_order, name = "update_order"),

    path('update_order_status/<int:id>/<str:order_status>/', views.update_order_status, name = "update_order_status"),
    









]