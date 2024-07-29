from django.shortcuts import render,redirect
from shop.form import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json
# Create your views here.
def home(request):
    catagory=Catagory.objects.filter(status=0)
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"catagory":catagory,"products":products})

def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method=="POST":
            name=request.POST.get("username")
            pwd=request.POST.get("password")
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("home")
            else:
                messages.error(request,"Invalid User Name or Password") 
                return redirect("login")
        return render(request,"shop/login.html")

def register(request):
    form=CustomUserForm()   
    if request.method == "POST":
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You can Login Now!")
            return redirect("login")
    return render(request,"shop/register.html",{"form":form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request,"shop/collection.html",{"catagory":catagory})

def collectionsview(request,name):
    catagory=Catagory.objects.filter(status=0)
    if(Catagory.objects.filter(name=name,status=0)):
        products=Product.objects.filter(catagory__name=name)
        return render(request,"shop/products/index.html",{"catagory":catagory,"products":products,"catagory_name":name})
    else:
        messages.warning(request,"No Such Catagory Found")
        return redirect("collections") 
    
def product_details(request,cname,pname):
    catagory=Catagory.objects.filter(status=0)
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{"catagory":catagory,"products":products})
        else:
            messages.error(request,"No Such Products Found")
            return render("collections")
    else:
            messages.error(request,"No Such Products Found")
            return render("collections") 
        
        
def add_to_cart(request):
    if request.headers.get("X-Requested-Width")=="XMLHttpRequest":
        if request.user.is_authenticated:
            data=json.load(request)
            product_qty=data['product_qty']
            product_id=data['pid']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({"status":"Product Already in Cart"},status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({"status":"Product Added to Cart"},status=200)
                    else:
                        return JsonResponse({"status":"Product Stock not Avaliable"},status=200)
            
        else:
            return JsonResponse({"status":"Login to Add Cart"},status=200)        
    else:
        return JsonResponse({"status":"Invalid Access"},status=200)
    
    
def cart_page(request):
    catagory=Catagory.objects.filter(status=0)
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"catagory":catagory,"cart":cart})
    else:
        return redirect("home")
        
def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("cart")
    
        
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect("home")
        