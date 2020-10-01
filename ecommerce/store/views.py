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
from . utils import cookieCart, cartData, guestOrder
import requests
import razorpay

# Create your views here.


def otp(request):
    if request.method == 'GET':
        phone = request.COOKIES['mobile']
        print(phone)
        user = User.objects.filter(last_name = phone).exists()
        print(user)
        if not user:
            messages.info(request,'Mobile number invalid')
            return redirect('mobile')
            
        url = "https://d7networks.com/api/verifier/send"

        num = str(91)+phone

        payload = {'mobile': num,
        'sender_id': 'SMSINFO',
        'message': 'Your otp code is {code}',
        'expiry': '900'}
        files = [

        ]
        headers = {
        'Authorization': 'Token 3202b5c476f743ea70714e6e31e62c17fdad14b0'
        }

        response = requests.request("POST", url, headers=headers, data = payload, files = files)

        print(response.text.encode('utf8'))
        otp_id = response.text[11:47] 
        print(otp_id)                                                          
        responce  = render(request, 'store/otp.html')
        responce.set_cookie('otp_id', otp_id)
        return responce
    else:

        otp = request.POST.get('otp')
        print(otp)

        otp_id = request.COOKIES['otp_id']

        url = "https://d7networks.com/api/verifier/verify"

        payload = {'otp_id': otp_id,
        'otp_code': otp}
        files = [

        ]
        headers = {
        'Authorization': 'Token 3202b5c476f743ea70714e6e31e62c17fdad14b0'
        }

        response = requests.request("POST", url, headers=headers, data = payload, files = files)

        b = json.loads(response.text)
        try:
            print(b["status"])
        except:
            b["status"] = 'failed'
            print(b["status"])
        if (b["status"] == "success"):
            phone = request.COOKIES['mobile']
            user = User.objects.get(last_name = phone )
            print(user)
            username = user.username
            password = user.first_name
            print(password)
            print(username)
            user = auth.authenticate(request, username = username, password = password)
            print(user)
            if user is not None:
                auth.login(request,user)
                print('login request')
                return redirect('store')
            else:
                messages.info(request, 'OTP did not match')
                return redirect('mobile')
        print(response.text.encode('utf8'))
        messages.info(request, 'OTP did not match')
        return redirect('mobile')


def verify(request):
    if request.method == 'GET':
        url = "https://d7networks.com/api/verifier/verify"

        payload = {'otp_id': 'dca7f26e-240c-4262-a255-41bb4c967e38',
        'otp_code': '937786'}
        files = [

        ]
        headers = {
        'Authorization': 'Token 3202b5c476f743ea70714e6e31e62c17fdad14b0'
        }

        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        b = json.loads(response.text)
        print(b["status"])
        if (b["status"] == "success"):
            phone = request.COOKIES['mobile']
            user = User.objects.get(last_name = phone )
            user = auth.authenticate(request, last_name = phone)

            if user is not None:
                auth.login(request,user)
                print('login request')
                return redirect('store')
            else:
                messages.info(request, 'Invalid credentials')

        print(response.text.encode('utf8'))
        return render(request, 'store/otp.html')
    return render(request, 'store/otp.html')
        
def mobile(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        print(mobile)
        responce = redirect('otp')
        responce.set_cookie('mobile', mobile)
        return responce

    return render(request, 'store/mobile.html')

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
     if request.method == 'POST':  

        username = request.POST['username']
        email = request.POST['email']
        mobile = request.POST['mobile']
        password1 = request.POST['password']
        password2 = request.POST['password0']
        

        if password1==password2 :
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return render(request, 'store/register.html')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'email taken')
                return render(request, 'store/register.html')
            elif User.objects.filter(last_name=mobile).exists():
                messages.info(request, 'email taken')
                return render(request, 'store/register.html')
            else:    
                user = User.objects.create_user(username = username, password = password1, email = email,first_name = password1, last_name = mobile)
                user.save();
                print('User created')
                return redirect('login')
                
        else:
            messages.info(request, 'password not matching')       
            return render(request, 'store/register.html')
       

     else:
        return render(request, 'store/register.html')

def store(request):

    if request.user.is_superuser:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    elif request.user.is_authenticated:

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
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    Data = cartData(request)
    cartItems = Data['cartItems']
    order = Data['order']
    items = Data['items']

    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    url = "https://restcountries-v1.p.rapidapi.com/all"

    headers = {
        'x-rapidapi-host': "restcountries-v1.p.rapidapi.com",
        'x-rapidapi-key': "3b2ed275fbmsh21f27fe96f38688p182fedjsna34ff216cf39"
        }

    response = requests.request("GET", url, headers=headers)

    c = json.loads(response.text)
    print(c[0]["name"])

    client  = razorpay.Client(auth=("rzp_test_aVR1IKDghGVJcq", "MIdgCBvppW3DYwzXqIgRNjcd"))

    Data = cartData(request)
    cartItems = Data['cartItems']
    order = Data['order']
    items = Data['items']
    print('order:',order)
    if request.user.is_authenticated:
        total = int(order.get_cart_total*100)
    else:
        total = int(order['get_cart_total']*100)
    # toal = order.get_cart_total
    order_amount = total
    order_currency = 'USD'
    order_receipt = 'order_rcptid_11'
    
    response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt,payment_capture = 0) )

    print(response)
    order_id = response['id']
    order_status = response['status']
    context = {'items': items, 'order':order, 'cartItems':cartItems, 'order_id':order_id,'c':c}
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
        customer, order = guestOrder(request, data)

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

def orders(request):
    customer = request.user.customer
    print(customer)
    order = Order.objects.filter(customer = customer)
    print(order[0])
    orderitems = OrderItem.objects.filter(order = order[0])
    print(orderitems[0].product.name)
    print(orderitems[0].product.price)
    print(orderitems[0].quantity)

    items = []

    for i in order:
        details = OrderItem.objects.filter(order = i)
        print('details:',details)
        for j in details:
            print('j:',j.product)
            items.append(j)
    
    for k in items:
        print('items:',k)
        print('name:',k.product.name)
        print('price:',k.product.price)
        print('quantity:',k.quantity)
        print('date:',k.order.date_ordered)
    


    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        # items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        context = {'cartItems':cartItems}
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
        
    context = {'cartItems':cartItems,'items':items}
 

    return render(request, 'store/orders.html', context)

# Admin's section

def admin_login(request):

    return render(request, 'store/admin_login.html')
