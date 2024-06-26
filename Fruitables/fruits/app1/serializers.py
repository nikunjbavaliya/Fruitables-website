from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import User, Contact, Product, Checkout, Cart, Reply
import re


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        confirmpassword = data.get("confirmpassword")
        phone_number = data.get("phone_number")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        if len(str(phone_number)) != 10:
            raise ValidationError("Phone number is not valid")
        if password != confirmpassword:
            raise ValidationError("Passwords do not match")

        return data

    def create(self, validated_data):
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "password")

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        person_details = User.objects.filter(
            username=username, password=password
        ).first()
        if not person_details:
            raise ValidationError("Invalid Username or Password")
        return data


class ForgotSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("email",)

    def validate(self, data):
        email = data.get("email")
        person_details = User.objects.filter(email=email)
        if not person_details:
            raise serializers.ValidationError("email address not valid")
        return data


class OtpSerializer(serializers.Serializer):
    enter_otp = serializers.CharField()

    def validate(self, data):
        otp = self.context.get("otp")
        enter_otp = data.get("enter_otp")
        if otp != enter_otp:
            raise serializers.ValidationError("Invalid OTP")
        return data


class ResetpasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("password", "confirmpassword")

    def validate(self, data):
        email = self.context.get("email_id")
        password = data.get("password")
        confirmpassword = data.get("confirmpassword")

        if password != confirmpassword:
            raise ValidationError("password not match")

        person_details = User.objects.get(email=email)
        person_details.password = password
        person_details.confirmpassword = confirmpassword
        person_details.save()
        return person_details


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ("yourname", "email", "message")

    def validate(self, data):
        yourname = data.get("yourname")

        if Contact.objects.filter(yourname=yourname).exists():
            raise ValidationError("Username already exists")
        return data

    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        return contact


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "product_name",
            "product_price",
            "product_quantity",
            "product_img",
            "product_details",
            "product_id",
        )


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            "product_name",
            "product_price",
            "product_quantity",
            "product_img",
            "product_details",
            "product_id",
            "id",
        )


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2
    )

    class Meta:
        model = Cart
        fields = ("product_name", "product_price", "product_quantity")


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"

class EditprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("fullname", "phone_number")

    def validate(self, data):
        username = self.context.get("user_id")
        fullname = data.get("fullname")
        phone_number = data.get("phone_number")

        # Check if phone_number contains only digits
        if not phone_number.isdigit():
            raise ValidationError("Please enter only numbers for the phone number.")

        # Check if phone_number length is 10 digits
        if len(phone_number) != 10:
            raise ValidationError("Enter a 10 digit phone number.")

        # Update the user's profile if exists
        person_details = User.objects.filter(username=username).first()
        if person_details:
            person_details.fullname = fullname
            person_details.phone_number = phone_number
            person_details.save()
        return data
