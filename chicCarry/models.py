from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def total_rating(self):
        """
        Calculates the total rating for the product by summing up all the ratings
        from its related reviews.
        """
        return self.reviews.aggregate(total=models.Sum('rating'))['total'] or 0

class Cart(models.Model):
    class CartStatus(models.TextChoices):
        ACTIVE = 'Active', _('Active')
        PAID = 'Paid', _('Paid')
        CANCELLED = 'Cancelled', _('Cancelled')
        ORDERED = 'Ordered', _('Ordered')  # Add this line for ORDERED status

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    status = models.CharField(max_length=20, choices=CartStatus.choices, default=CartStatus.ACTIVE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

  
    @property
    def total_price(self):
        # Sum the total price of all the cart items
        return sum(item.total_price for item in self.cart_items.all())

    def save(self, *args, **kwargs):
        if self.status == Cart.CartStatus.ACTIVE:
            # Ensure only one active cart per user
            Cart.objects.filter(user=self.user, status=Cart.CartStatus.ACTIVE).exclude(id=self.id).update(status=Cart.CartStatus.ORDERED)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Cart {self.id} - {self.user.username} - {self.status}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}, {self.state}, {self.country}"


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        COMPLETED = 'Completed', _('Completed')
        FAILED = 'Failed', _('Failed')

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'Credit Card', _('Credit Card')
        PAYPAL = 'PayPal', _('PayPal')
        STRIPE = 'Stripe', _('Stripe')
        BANK_TRANSFER = 'Bank Transfer', _('Bank Transfer')
        CASH_ON_DELIVERY = 'Cash on Delivery', _('Cash on Delivery')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    cart = models.OneToOneField('Cart', on_delete=models.CASCADE, related_name='payment')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, choices=PaymentMethod.choices)  # Using the PaymentMethod choices
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Review for {self.product.name} by {self.user.username}'

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_products')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} in {self.user.username}\'s wishlist'
