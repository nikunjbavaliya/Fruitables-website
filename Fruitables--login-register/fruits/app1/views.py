from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from rest_framework import serializers, generics, status
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ForgotSerializer,
    ResetpasswordSerializer,
    OtpSerializer,
    ContactSerializer,
    ProductSerializer,
    CheckoutSerializer,
)
from .models import Product, CategoryChoices, Cart, User
from typing import Union
from rest_framework.request import Request
from django.http.request import HttpRequest
import random
from django.db.models import Sum, Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "register.html"

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("register")
        return render(request, self.template_name)

    def post(self, request: Union[Request, HttpRequest]) -> Union[redirect, render]:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("login")
        messages.error(request, serializer.errors["non_field_errors"][0])
        return render(request, self.template_name)


class LoginView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LoginSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "login.html"

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")
        return render(request, self.template_name)

    def post(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get("username")
            request.session["username"] = username
            return redirect("index")
        messages.error(request, serializer.errors["non_field_errors"][0])
        return render(request, self.template_name)


class IndexView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "index.html"

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
            if "username" not in request.session:
                return redirect("login")

            query = request.GET.get('q')
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')

            products = Product.objects.all()

            if query:
                products = products.filter(product_name__icontains=query)
            if min_price:
                products = products.filter(product_price__gte=min_price)
            if max_price:
                products = products.filter(product_price__lte=max_price)

            fruits = products.filter(product_category=2)
            veg = products.filter(product_category=1)

            return render(
                request,
                self.template_name,
                context={
                    "all_product": products,
                    "veg": veg,
                    "fruits": fruits,
                },
            )


class ForgotView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "forgot.html"
    serializer_class = ForgotSerializer

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")
        return render(request, self.template_name)

    def post(self, request: Union[Request, HttpRequest]) -> redirect:
        serializer = ForgotSerializer(data=request.data)
        if not serializer.is_valid():
            return redirect("forgot")
        email = serializer.data["email"]
        otp = str(random.randint(1000, 9999))
        request.session["email"] = email
        request.session["otp"] = otp
        email_subject = "Fruitables otp"
        email_body = f"Your Otp {otp}"
        email = EmailMessage(email_subject, email_body, to=[email])
        email.send()
        return redirect("otp")


class OtpView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "otp.html"
    serializer_class = OtpSerializer

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")
        return render(request, self.template_name)

    def post(self, request: Union[Request, HttpRequest]) -> redirect:
        otp = request.session.get("otp")
        serializer = OtpSerializer(data=request.data, context={"otp": otp})
        if not serializer.is_valid():
            messages.error(request, serializer.errors["non_field_errors"][0])
            return redirect("otp")
        return redirect("reset")


class ResetPasswordView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "reset_password.html"
    serializer_class = ResetpasswordSerializer

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")
        return render(request, self.template_name)

    def post(self, request: Union[Request, HttpRequest]) -> redirect:
        email = request.session.get("email")
        serializer = ResetpasswordSerializer(
            data=request.data, context={"email_id": email}
        )
        if not serializer.is_valid():
            messages.error(request, serializer.errors["non_field_errors"][0])
            return redirect("reset")
        return redirect("login")


class ShopView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "shop.html"

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")

        min_price = request.GET.get("min_price", 0)
        max_price = request.GET.get("max_price", 500)

        fruits = Product.objects.filter(product_category=CategoryChoices.FRUITS)
        veg = Product.objects.filter(product_category=CategoryChoices.VEGETABLES)

        if min_price or max_price:
            fruits = fruits.filter(
                product_price__gte=min_price, product_price__lte=max_price
            )
            veg = veg.filter(product_price__gte=min_price, product_price__lte=max_price)

        fruit_stock_counts = fruits.values("product_name").annotate(
            total_stock=Sum("product_quantity")
        )

        fruits_serialized = ProductSerializer(fruits, many=True)
        veg_serialized = ProductSerializer(veg, many=True)

        singal_fruit = Product.objects.filter(product_category=CategoryChoices.FRUITS)[:3]
        singal_veg = Product.objects.filter(product_category=CategoryChoices.VEGETABLES).first()

        return render(
            request,
            self.template_name,
            context={
                "fruits": fruits_serialized.data,
                "veg": veg_serialized.data,
                "fruit_stock_counts": fruit_stock_counts,
                "min_price": min_price,
                "max_price": max_price,
                "singal_fruit": singal_fruit,
                "singal_veg": singal_veg,
            },
        )

    def post(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("index")

        selected_category = request.POST.get("Categories-1", None)
        products = Product.objects.all()  

        if selected_category:
            if selected_category == "Organic":
                products = products.filter(product_category=CategoryChoices.ORGANIC)
            elif selected_category == "Fresh":
                products = products.filter(product_category=CategoryChoices.FRESH)
            elif selected_category == "Sales":
                products = products.filter(product_category=CategoryChoices.SALES)
            elif selected_category == "Discount":
                products = products.filter(product_category=CategoryChoices.DISCOUNT)
            elif selected_category == "Expired":
                products = products.filter(product_category=CategoryChoices.EXPIRED)

        search_query = request.POST.get("search_query", "")
        min_price = request.POST.get("min_price", 0)
        max_price = request.POST.get("max_price", 500)

        if search_query:
            search_results = Product.objects.filter(
                Q(product_name__icontains=search_query),
                Q(product_price__gte=min_price),
                Q(product_price__lte=max_price),
            )
        else:
            search_results = Product.objects.filter(
                Q(product_price__gte=min_price), Q(product_price__lte=max_price)
            )

        search_results_serialized = ProductSerializer(search_results, many=True)
        fruits = Product.objects.filter(product_category=CategoryChoices.FRUITS)
        veg = Product.objects.filter(product_category=CategoryChoices.VEGETABLES)

        fruit_stock_counts = fruits.values("product_name").annotate(
            total_stock=Sum("product_quantity")
        )

        return render(
            request,
            self.template_name,
            context={
                "search_results": search_results_serialized.data,
                "search_query": search_query,
                "fruits": fruits,
                "veg": veg,
                "fruit_stock_counts": fruit_stock_counts,
                "min_price": min_price,
                "max_price": max_price,
                "products": products,
                "selected_category": selected_category,
            },
        )
    
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        user = User.objects.get(username=request.session["username"])
        product = get_object_or_404(Product, product_id=product_id)
        
        cart_item, created = Cart.objects.get_or_create(person=user, product=product)
        
        if not created:
            cart_item.product_quantity += 1
            cart_item.save()
        
        return redirect('cart')

class CartView(LoginRequiredMixin, View):
    template_name = 'cart.html'
    
    def get(self, request):
        user = User.objects.get(username=request.session["username"])
        cart_items = Cart.objects.filter(person=user)
        
        cart_subtotal = 0
        for item in cart_items:
            item.total_price = item.product.product_price * item.product_quantity
            cart_subtotal += item.total_price
        
        shipping_cost = 30 
        cart_total = cart_subtotal + shipping_cost

        return render(request, self.template_name, {
            'cart_items': cart_items,
            'cart_subtotal': cart_subtotal,
            'shipping_cost': shipping_cost,
            'cart_total': cart_total,
        })

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        user = User.objects.get(username=request.session["username"])
        product = get_object_or_404(Product, product_id=product_id)
        cart_item = get_object_or_404(Cart, person=user, product=product)
        cart_item.delete()
        
        return redirect('cart')
    

class ProdcutdetailView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "shop-detail.html"

    def get(self, request, product_id):
        if "username" not in request.session:
            return redirect("login")

        product = Product.objects.filter(product_id=product_id).first()
        if not product:
            return redirect("shop")

        return render(request, "shop-detail.html", {"product_details": product})

    # def post(self, request, product_id):
    #     if "username" not in request.session:
    #         return redirect("login")

    #     product = Product.objects.filter(product_id=1)
    #     if not product:
    #         return redirect("shop")

    #     return redirect("product", product_id=product_id)


class ContactView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "contact.html"

    def get(self, request: Union[Request, HttpRequest]) -> Union[render, redirect]:
        if "username" not in request.session:
            return redirect("login")
        serializer = ContactSerializer()
        return render(request, self.template_name, {"serializer": serializer})

    def post(self, request: Union[Request, HttpRequest]) -> Union[redirect, render]:
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("index")
        return render(request, self.template_name)


class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "checkout.html"

    def get(self, request, *args, **kwargs):
        if "username" not in request.session:
            return redirect("login")
        serializer = CheckoutSerializer()
        return render(request, self.template_name, {"serializer": serializer})

    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("index") 
        return render(request, self.template_name, {"serializer": serializer})
    
def testimonial(request):
    return render(request, "testimonial.html")


def error(request):
    return render(request, "404.html")
