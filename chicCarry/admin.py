from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Wishlist)


