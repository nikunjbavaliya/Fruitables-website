from django.db import models


class User(models.Model):

    fullname = models.CharField(max_length=150, default="")
    username = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    confirmpassword = models.CharField(max_length=50)
    otp = models.CharField(max_length=4, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.fullname} - {self.email}"


class CategoryChoices(models.IntegerChoices):
    ALL = 0, "ALL"
    VEGETABLES = 1, "Vegetables"
    FRUITS = 2, "Fruits"


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    product_price = models.IntegerField()
    product_quantity = models.IntegerField()
    product_img = models.ImageField(upload_to="image", default=None)
    product_details = models.CharField(max_length=500)
    product_id = models.CharField(primary_key=True, max_length=5)
    product_category = models.IntegerField(
        choices=CategoryChoices.choices, default=CategoryChoices.ALL
    )

    def __str__(self):
        return self.product_name


class Contact(models.Model):

    yourname = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    message = models.TextField(max_length=500)


class Cart(models.Model):

    person = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_quantity = models.PositiveIntegerField(default=1)


class Checkout(models.Model):
    fullname = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    create_account = models.BooleanField(default=False)
    ship_to_different_address = models.BooleanField(default=False)
    order_notes = models.TextField(blank=True, null=True)
    direct_bank_transfer = models.BooleanField(default=False)
    check_payments = models.BooleanField(default=False)
    cash_on_delivery = models.BooleanField(default=False)
    paypal = models.BooleanField(default=False)

    def __str__(self):
        return f"Checkout - {self.fullname}"
