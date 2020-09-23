from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User,auth
# Create your views here.

def login(request):

    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(password)
            print('username')
            print('user login')
            user = auth.authenticate(request, username = username, password = password)

            if user is not None:
                auth.login(request,user)
                print('login request')
                return redirect('store')
            else:
                messages.info(request, 'Invalid credentials')
        return render(request, 'store/login.html')

def logout (request):
    auth.logout(request)
    return redirect('store')

def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form':form}
    return render(request, 'store/register.html', context)

def store(request):

    if request.user.is_authenticated:

        login_user = request.user
        login_name = request.user.username
        login_email = request.user.email
        print(login_user)
        print(login_name)
        print(login_email)
        customer, created = Customer.objects.get_or_create(user = login_user, name = login_name, email = login_email)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print('cart:', cart)  
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print('cart:', cart)        
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

        for i in cart:
            cartItems += cart[i]['quantity']

            try:
                # cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id':product.id,
                    'product':{'id':product.id,'name':product.name, 'price':product.price, 
                    'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
                    'digital':product.digital,'get_total':total,
                    }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass


    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)

    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added', safe=False)

def processOrder(request):

    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAdress.objects.create(

                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode']
            )
        
    else:
        print('User is not logged in')
    print('Data:',request.body)
    return JsonResponse('Payment Complete!', safe=False)

def product(request, pk):
 if request.user.is_authenticated:
    product = Product.objects.get(id=pk)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {'product': product, 'cartItems':cartItems}
 else:
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('cart:', cart)  
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']
     
    product = Product.objects.get(id=pk)
    context = {'product': product, 'cartItems':cartItems}


 return render(request, 'store/product.html', context)