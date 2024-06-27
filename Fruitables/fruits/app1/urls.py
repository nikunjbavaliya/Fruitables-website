from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    IndexView,
    ForgotView,
    OtpView,
    ResetPasswordView,
    ShopView,
    ProdcutdetailView,
    ContactView,
    AddToCartView,
    CartView,
    RemoveFromCartView,
    CheckoutView,
)   

from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("index/", IndexView.as_view(), name="index"),
    path("forgot/", ForgotView.as_view(), name="forgot"),
    path("otp/", OtpView.as_view(), name="otp"),
    path("reset/", ResetPasswordView.as_view(), name="reset"),
    path("shop/", ShopView.as_view(), name="shop"),
    path("product/<int:product_id>/", ProdcutdetailView.as_view(), name="shopdetail"),
    path("add_to_cart/<int:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/", CartView.as_view(), name="cart"),
    path(
        "remove_cart/<int:product_id>/",
        RemoveFromCartView.as_view(),
        name="remove_cart",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("contact/", ContactView.as_view(), name="contact"),
    #####################################################

    path("404/", views.error, name="404"),
    path("testimonial/", views.testimonial, name="testimonial"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
