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
from django.core.files.storage import FileSystemStorage
from datetime import *
from django.contrib.auth.decorators import login_required
import base64
from PIL import Image
from base64 import decodestring
import binascii
from django.core.files import File
from django.core.files.base import ContentFile

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
                responce = redirect('otp')
                responce.set_cookie('mobile', mobile)
                return responce
                
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

    countries = json.loads(response.text)
    print(countries[8]['name'])
    print(countries[8]["callingCodes"])

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
    
    order_amount = total
    order_currency = 'USD'
    order_receipt = 'order_rcptid_11'
    if order_amount == 0:
        return redirect('cart')
    else:
        response = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt,payment_capture = 0) )

        print(response)
        order_id = response['id']
        order_status = response['status']
        context = {'items': items, 'order':order, 'cartItems':cartItems, 'order_id':order_id,'c':countries}
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

    transaction_id = datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)

        country = data['shipping']['country']
        countrycode = CountryCodes.objects.get(country = country)
        code = countrycode.code
        print(code)

        if order.shipping == True:
            ShippingAdress.objects.create(

                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
                country = code

                
            )
        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if round(total,2) == round(order.get_cart_total,2):
        order.complete = True
    order.save()
    
    country = data['shipping']['country']
    countrycode = CountryCodes.objects.get(country = country)
    code = countrycode.code
    print(code)

    if order.shipping == True:
        ShippingAdress.objects.create(

            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
            country = code

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
    order = Order.objects.filter(customer = customer,complete=True)
   


    items = []

    for i in order:
        details = OrderItem.objects.filter(order = i,product__isnull=False)
        print('details:',details)
        for j in details:
            print('j:',j.product)
            items.append(j)
    

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == "tishil" and password =="1234":
            user = auth.authenticate(request, username = username, password = password)

            if user is not None:
                auth.login(request,user)
                return redirect('admin_home')
            else:
                messages.info(request, 'Invalid credentials')
                return render(request, 'store/admin_login.html')
        messages.info(request, 'Invalid credentials')
        return render(request, 'store/admin_login.html')

    return render(request, 'store/admin_login.html')

def admin_logout(request):
    auth.logout(request)
    return redirect('admin_login')

@login_required(login_url='/admin_login/')
def admin_home(request):

    year = datetime.now().year
    month = datetime.now().month
    print(month)
    chart_order = Order.objects.filter(date_ordered__year = year,date_ordered__month = month)
    print(chart_order[0].get_cart_total)

    chart_values = []
    
    for i in range(0,6):
        chart_order = Order.objects.filter(date_ordered__year = year,date_ordered__month = month-5+i)
        order_total = 0
        for items in chart_order:
            try:
                order_total += round(items.get_cart_total,2)
            except:
                order_total += 0
        chart_values.append(round(order_total,2))        
    print(chart_values)

    orders = Order.objects.all()
    total = 0
    for order in orders:
        try:
            order_total = order.get_cart_total
        except:
            order_total = 0
        total = total + order_total
    
    print('total',round(total,2))

    customer = Customer.objects.count()
    product = Product.objects.count()
    order_count = Order.objects.count()

    context ={'customer':customer,'product':product,'order_count':order_count,'total':total,'chart_values':chart_values}

    return render(request,"admin/home_content.html", context)


@login_required(login_url='/admin_login/')
def product_view(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,"admin/product_view.html", context)


@login_required(login_url='/admin_login/')
def add_product(request):
    if request.method == 'POST':

        name = request.POST['name']
        price = request.POST['price']
        product_type = request.POST['product_type']
        image_data =request.POST['image64data']
        print('data', image_data)
        value = image_data.strip('data:image/png;base64,')
        
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]

        data = ContentFile(base64.b64decode(imgstr),name='temp.' + ext)

        item = Product(name = name,price = price, digital = product_type, image = data)
        item.save();
     
        products = Product.objects.all()
        context = {'products':products}
        return render(request,"admin/product_view.html", context)
    return render(request,"admin/add_product.html")


@login_required(login_url='/admin_login/')
def update_product(request,id):
    print(id)
    product = Product.objects.get(id = id)
    print('product:',product.name)
    context = {'products':product}
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        product_type = request.POST['product_type']
        image=request.FILES.get('myfile')
      
        product.name = name
        product.price = price
        product.digital = product_type
    
        if 'myfile' not in request.POST:
            product.image=request.FILES['myfile']
        else:
            product.image = product.image   
        product.save();
        
        return redirect('product_view')
    else:
        
        return render(request,"admin/update_product.html",{'product':product})
    

@login_required(login_url='/admin_login/')
def delete_product(request,id):
    product = Product.objects.get(id = id)
    product.delete()
    return redirect('product_view')


@login_required(login_url='/admin_login/')
def orders_view(request):
    orders = Order.objects.all()
    
    context = {'orders':orders}
    return render(request,"admin/orders_view.html", context)


@login_required(login_url='/admin_login/')
def orderitems_view(request):
    orderitems = OrderItem.objects.filter(product__isnull=False)
    
    context = {'orderitems':orderitems}
    return render(request,"admin/orderitems_view.html", context)



def update_order_status(request,id,order_status):
    print(id)
    
    order = Order.objects.get(id = id)
    order.order_status = order_status
    order.save();

    return redirect('orders_view')

@login_required(login_url='/admin_login/')
def shipping_view(request):
    shipping = ShippingAdress.objects.all()
    
    context = {'shipping':shipping}
    return render(request,"admin/shipping_view.html", context)


@login_required(login_url='/admin_login/')
def users_view(request):
    users = User.objects.all()
    print(users)
    context = {'users':users}
    return render(request,"admin/users_view.html", context)


@login_required(login_url='/admin_login/')
def customer_view(request):
    customers = Customer.objects.all()

    items = []

    for customer in customers:
        order = Order.objects.filter(customer = customer,complete = True)
        value = order.count()
        items.append(value)
    
    data = zip(customers,items)

    
    print(customers)
    return render(request,"admin/customer_view.html", {'data':data})