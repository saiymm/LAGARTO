from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')  # Fields to display in the admin list view
    search_fields = ('name',)  # Enable search functionality
    ordering = ('name',)  # Default ordering

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'created_at', 'updated_at')
    list_filter = ('category',)  # Filter by category
    search_fields = ('name', 'description')  # Enable search by name and description
    ordering = ('name',)  # Default ordering

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'phone_number', 'date_joined')
    search_fields = ('user__username', 'address')  # Enable search by username and address
    ordering = ('user__username',)  # Default ordering

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'shipping_address', 'total_price', 'status')
    list_filter = ('status', 'order_date')  # Filter by status and order date
    search_fields = ('customer__user__username', 'shipping_address')  # Enable search by customer and address
    ordering = ('-order_date',)  # Default ordering (newest orders first)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__customer__user__username', 'product__name')  # Search by customer or product name
    ordering = ('order',)  # Default ordering

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'rating', 'created_at')
    list_filter = ('rating',)  # Filter by rating
    search_fields = ('product__name', 'customer__user__username')  # Search by product or customer
    ordering = ('-created_at',)  # Default ordering (newest reviews first)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'added_at')
    search_fields = ('customer__user__username', 'product__name')  # Search by customer or product name
    ordering = ('-added_at',)  # Default ordering (newest items first)
