from django.contrib import admin
from .models import User, Product, Contact, Cart, Checkout


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "fullname",
        "email",
        "password",
    )


admin.site.register(User, PersonAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "product_price",
        "product_quantity",
        "product_img",
        "product_details",
        "product_id",
        "product_category",
        "product_description"
    )
    search_fields = ("product_name",)


admin.site.register(Product, ProductAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ("yourname", "email", "message")


admin.site.register(Contact, ContactAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ("person", "product", "product_quantity")


admin.site.register(Cart, CartAdmin)


class CheckoutAdmin(admin.ModelAdmin):
    list_display = ("fullname", "email", "city")


admin.site.register(Checkout, CheckoutAdmin)
