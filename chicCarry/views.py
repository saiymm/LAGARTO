from datetime import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import CustomAuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import CustomUserCreationForm 
from .forms import CustomUserChangeForm 
from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import ListView, RedirectView
from django.views.generic.edit import DeleteView
from .models import Cart, CartItem, Product
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from .models import *
from django.views import View
from django.db.models import Avg, Sum
from .models import Payment, Review
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Group

# Use timezone.now() to get the current time with respect to the timezone
current_time = timezone.now()

class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # Use the custom form
    template_name = 'chicCarry/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)  # Automatically log in the user after registration
        
        # Create a new Customer instance and link it to the user
        Customer.objects.create(user=user)
        
        # Add the user to the "User" group
        user_group = Group.objects.get(name='User')  # Get the "User" group
        user.groups.add(user_group)  # Add the user to the group
        
        return response

# Login view
class LoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'chicCarry/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Administrator').exists():
            return reverse_lazy('dashboard')  # Redirect to the admin dashboard
        elif user.groups.filter(name='User').exists():
            return reverse_lazy('profile')  # Redirect to the user dashboard
        return reverse_lazy('homepage')  # Default redirect to profile page if neither


    
def logoutstudent(request):
    # Perform the logout operation
    logout(request)  # Logs out the user
    return redirect("login")  # Redirects to the login page




class HomePageView(TemplateView):
    template_name = "chicCarry/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()  # Fetch all products from the database
        return context

class AboutPageView(TemplateView):
    template_name = "chicCarry/aboutpage.html"

class UserProductListView(ListView):
    model = Product
    template_name = 'chicCarry/user_product_list.html'  # Your template for listing products
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add the most recent products to the context
        recent_products = Product.objects.all().order_by('-created_at')[:5]  # Adjust the limit as needed
        context['recent_products'] = recent_products

        # Add the highest-rated product to the context
        highest_rated_product = Product.objects.annotate(
            average_rating=Avg('reviews__rating')  # Calculate the average rating for each product
        ).order_by('-average_rating').first()  # Get the product with the highest average rating
        context['highest_rated_product'] = highest_rated_product

        # Add all reviews for the products
        reviews = Review.objects.all().select_related('product', 'user').order_by('-created_at')
        context['reviews'] = reviews

        return context
    

class UserProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'chicCarry/user_product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if the product is in the user's wishlist
        is_in_wishlist = Wishlist.objects.filter(user=self.request.user, product=self.object).exists()
        context['is_in_wishlist'] = is_in_wishlist

        # Add the highest review to the context
        highest_review = Review.objects.filter(product=self.object).order_by('-rating').first()
        context['highest_review'] = highest_review

        # Add the review form to the context
        context['review_form'] = ReviewForm()

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()  # Get the product object
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                # Create a review for the product
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()

                messages.success(request, 'Your review has been submitted successfully!')
                return redirect('user_product_detail', pk=product.pk)  # Redirect back to product detail page
            else:
                messages.error(request, 'Please fill out all fields.')
        else:
            messages.warning(request, 'You need to be logged in to submit a review.')
            return redirect('login')  # Redirect to login page if not authenticated
        
        # If the form isn't valid or user isn't authenticated, render the page with the form and product
        return render(request, self.template_name, {
            'product': product,
            'review_form': form,
            'is_in_wishlist': self.request.user.wishlist.filter(id=product.id).exists(),  # Pass wishlist status
        })


#userProfile


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'chicCarry/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Get the logged-in user
        customer = user.customer  # Access the associated Customer profile
        
        context['user'] = user
        context['customer'] = customer
        return context



class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm  # Use the updated form
    template_name = 'chicCarry/update_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Handle file upload for profile_picture
        response = super().form_valid(form)
        if 'profile_picture' in self.request.FILES:
            customer, created = Customer.objects.get_or_create(user=self.request.user)
            customer.profile_picture = self.request.FILES['profile_picture']
            customer.save()
        login(self.request, self.object)  # Log the user back in
        return response
    
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'chicCarry/change_password.html'
    success_url = reverse_lazy('profile')  # Redirect to the profile page after successful password change

#HISTORY

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'chicCarry/payment_detail.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'  # Make sure it matches the URL parameter

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'chicCarry/payment_list.html'
    context_object_name = 'payments'

    # Overriding get_queryset to only show completed payments
    def get_queryset(self):
        return Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED)
#cartSystem

class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'chicCarry/view_cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # Get or create an active cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user, status=Cart.CartStatus.ACTIVE)
        return cart.cart_items.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the active cart for the user
        cart = Cart.objects.filter(user=self.request.user, status=Cart.CartStatus.ACTIVE).first()

        # If no cart or no items in the cart, pass an empty cart message
        if not cart or not cart.cart_items.exists():
            context['empty_cart'] = "Your cart is empty. Start adding items to begin a new transaction!"
            context['cart'] = None
            context['total_price'] = 0
        else:
            context['cart'] = cart
            context['total_price'] = cart.total_price

        return context

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'chicCarry/address_form.html'
    success_url = reverse_lazy('address_list')  # Redirect after success

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user  # Set the user to the logged-in user

        if address.is_default:
            # Make sure only one default address exists per user
            Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
        
        address.save()
        messages.success(self.request, 'Your address has been saved successfully.')
        return super().form_valid(form)
    
class AddressListView(ListView):
    model = Address
    template_name = 'chicCarry/address_list.html'
    context_object_name = 'addresses'  # Default is 'object_list'
    
    def get_queryset(self):
        # Filter addresses based on the logged-in user
        return Address.objects.filter(user=self.request.user)
    
class AddressUpdateView( LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'chicCarry/address_form.html'
    context_object_name = 'address'

    def get_success_url(self):
        messages.success(self.request, 'Your address has been updated successfully.')
        return reverse_lazy('address_list')  # Redirect after success

    def form_valid(self, form):
        address = form.save(commit=False)
        if address.is_default:
            # Ensure only one default address exists per user
            Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
        address.save()
        return super().form_valid(form)

class UpdateCartQuantityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Get the cart item based on the primary key (pk)
        cart_item = get_object_or_404(CartItem, pk=pk)

        # Make sure the cart item belongs to the current user's cart
        if cart_item.cart.user != request.user:
            raise Http404("You cannot edit items from another user's cart.")

        # Get the new quantity from the form submission
        new_quantity = int(request.POST.get('quantity'))

        # Ensure the new quantity is valid (positive number)
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()

        # Redirect back to the cart page
        return redirect('view_cart')

class AddToCartView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Check for an active cart
        cart = Cart.objects.filter(user=self.request.user, status=Cart.CartStatus.ACTIVE).first()

        # If no active cart exists or the cart is empty, create a new one
        if not cart or not cart.cart_items.exists():
            cart = Cart.objects.create(user=self.request.user, status=Cart.CartStatus.ACTIVE)
        else:
            # Update the updated_at field manually if needed
            cart.updated_at = timezone.now()
            cart.save()

        # Add the product to the cart or update its quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return reverse_lazy('view_cart')

    

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            # Find the CartItem based on item_id and the current user
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            # Remove the item from the cart
            cart_item.delete()
        except CartItem.DoesNotExist:
            # If item is not found, raise a 404 error
            raise Http404("Item not found")

        # Redirect to the cart page after the item is removed
        return redirect('view_cart')  # Ensure 'view_cart' is the correct URL name for the cart page


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'chicCarry/checkout.html'

    def get(self, request, *args, **kwargs):
        # Fetch the most recent cart for the user (assuming it's unpurchased)
        cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()


        total_price = cart.total_price

        context = {
            'cart': cart,
            'total_price': total_price,
        }
        return render(request, self.template_name, context)
    


class PaymentView(LoginRequiredMixin, View):
    template_name = 'chicCarry/payment.html'

    def get(self, request, *args, **kwargs):
        # Get the active cart for the user
        cart = Cart.objects.filter(user=request.user, status=Cart.CartStatus.ACTIVE).first()
        if not cart or not cart.cart_items.exists():
            raise Http404("No active cart found.")

        # Fetch the user's addresses
        addresses = Address.objects.filter(user=request.user)

        context = {
            'cart': cart,
            'total_price': cart.total_price,
            'addresses': addresses,
            'payment_methods': Payment.PaymentMethod.choices
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Get the active cart for the user
        cart = Cart.objects.filter(user=request.user, status=Cart.CartStatus.ACTIVE).first()
        if not cart:
            raise Http404("No active cart found.")

        # Get the selected address
        address_id = request.POST.get('address_id')
        if not address_id:
            return HttpResponseBadRequest("Address is required.")

        address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create a Payment instance
        payment_method = request.POST.get('payment_method', 'Unknown')
        payment = Payment.objects.create(
            user=request.user,
            cart=cart,
            address=address,
            amount=cart.total_price,
            payment_method=payment_method,
        )

        # Simulate payment processing (replace with actual logic)
        payment.status = Payment.PaymentStatus.COMPLETED
        payment.transaction_id = f"TXN-{payment.id}-{cart.id}"  # Example transaction ID
        payment.save()

        # Update cart status to PAID
        cart.status = Cart.CartStatus.PAID
        cart.save()

        # Debug: Log payment creation
        print(f"Payment created: ID={payment.id}, Cart ID={cart.id}, Amount={payment.amount}")

        # Redirect to payment success page
        return redirect('payment_success', payment_id=payment.id)

class PaymentSuccessView(LoginRequiredMixin, View):
    template_name = 'chicCarry/payment_success.html'

    def get(self, request, payment_id):
        # Debugging: Log the payment_id received
        print(f"PaymentSuccessView called with payment_id: {payment_id}")
        
        try:
            # Retrieve the payment based on payment_id and user
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)
            print(f"Payment found: ID={payment.id}, Amount={payment.amount}, User={payment.user.username}")
        except Http404:
            # Log the error if payment is not found
            print(f"Payment not found for ID={payment_id} and user={request.user.id}")
            return redirect('view_cart')  # Redirect to the cart or show an error message

        # Get cart details related to the payment (order)
        cart = payment.cart
        cart_items = cart.cart_items.all()
        total_price = cart.total_price  # Get total price from the cart

        # Proceed to render with all necessary context
        return render(request, self.template_name, {
            'payment': payment,
            'cart': cart,
            'cart_items': cart_items,
            'total_price': total_price
        })
    
#Wishlist

# View to display user's wishlist
class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'chicCarry/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        # Return wishlist items for the logged-in user
        return Wishlist.objects.filter(user=self.request.user)

# View to add a product to the wishlist
class AddToWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # Get the product object
        product = get_object_or_404(Product, id=product_id)
        
        # Check if the product is already in the user's wishlist
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            # Optionally show a message or redirect to another page
            return redirect(reverse('user_product_detail', kwargs={'pk': product_id}))
        
        # Add the product to the user's wishlist
        Wishlist.objects.create(user=request.user, product=product)
        
        # Redirect back to the product detail page after adding the item
        return redirect(reverse('user_product_detail', kwargs={'pk': product_id}))

# View to remove a product from the wishlist
class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # Get the product object
        product = get_object_or_404(Product, id=product_id)
        
        # Try to get the wishlist item for the logged-in user and the given product
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
        
        # If the item is found, delete it
        if wishlist_item:
            wishlist_item.delete()
        
        # Redirect back to the product detail page after removing the item
        return redirect(reverse('user_product_detail', kwargs={'pk': product_id}))

#adminside

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "chicCarry/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all payments and reviews
        payments = Payment.objects.all()
        reviews = Review.objects.all()

        # Calculate total amount and average rating
        total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        context['payments'] = payments
        context['reviews'] = reviews
        context['total_amount'] = total_amount
        context['average_rating'] = round(average_rating, 2)
        return context
    
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "chicCarry/user_list.html"
    context_object_name = 'users'  # The context variable name to use in the template
    ordering = ['username']  # Ordering users alphabetically by their username

# ListView: Display all products
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'chicCarry/product_list.html'  # Your template for listing products
    context_object_name = 'products'

# DetailView: Display a specific product's details
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'chicCarry/product_detail.html'  # Your template for product details
    context_object_name = 'product'

# CreateView: Add a new product
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'chicCarry/product_form.html'  # Your template for the product form
    fields = ['name', 'description', 'price', 'stock', 'category', 'image']  # Fields to display in the form
    success_url = reverse_lazy('product-list')  # Redirect after successful creation

# UpdateView: Edit an existing product
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'chicCarry/product_form.html'  # Your template for the product form
    fields = ['name', 'description', 'price', 'stock', 'category', 'image']  # Fields to display in the form
    success_url = reverse_lazy('product-list')  # Redirect after successful update

# DeleteView: Delete an existing product
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'chicCarry/product_confirm_delete.html'  # Your template for delete confirmation
    success_url = reverse_lazy('product-list')  # Redirect after successful deletion



# CreateView for adding a new category
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'chicCarry/category_form.html'  # Template for the category form
    fields = ['name', 'description']  # Fields to display in the form
    success_url = reverse_lazy('category-list')  # Redirect after successful creation

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'chicCarry/category_detail.html'  # Template for displaying the category details
    context_object_name = 'category'  # Context variable to use in the template

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'chicCarry/category_form.html'  # Reusing the same template as the create view
    fields = ['name', 'description']  # Fields to display in the form
    success_url = reverse_lazy('category-list')  # Redirect after successful update

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'chicCarry/category_list.html'  # Template for displaying categories
    context_object_name = 'categories'  # Context variable to use in the template

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'chicCarry/category_confirm_delete.html'  # Template for confirmation before deletion
    success_url = reverse_lazy('category-list')  # Redirect after successful deletion



