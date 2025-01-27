from django.urls import path
from .views import *
from . import views

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logoutstudent, name='logout'),  # Define the route for logout

    path('', HomePageView.as_view(), name='homepage'),
    path('about/', AboutPageView.as_view(), name='aboutpage'),
    path('userproductlist/', UserProductListView.as_view(), name='user-product-list'),  # List all products
    path('user/<int:pk>/', UserProductDetailView.as_view(), name='user-product-detail'),  # Product details


    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='update_profile'),  # URL for updating profile
    path('profile/change_password/', views.CustomPasswordChangeView.as_view(), name='change_password'),

    
    path('cart/', views.CartView.as_view(), name='view_cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:pk>/', views.UpdateCartQuantityView.as_view(), name='update_cart_quantity'),
    path('remove-item/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment/success/<int:payment_id>/', PaymentSuccessView.as_view(), name='payment_success'),

    path('address/create/', AddressCreateView.as_view(), name='address_create'),
    path('addresses/', AddressListView.as_view(), name='address_list'),
    path('address/edit/<int:pk>/', AddressUpdateView.as_view(), name='address_edit'),

    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),


    path('payment/<int:payment_id>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/completed/', PaymentListView.as_view(), name='payment_list'),

    path('product/<int:pk>/', views.UserProductDetailView.as_view(), name='user_product_detail'),




    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('users/', UserListView.as_view(), name='user_list'),

    path('productlist/', ProductListView.as_view(), name='product-list'),  # List all products
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),  # Product details
    path('create/', ProductCreateView.as_view(), name='product-create'),  # Create a product
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),  # Update a product
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),  # Delete a product


    path('category/add/', CategoryCreateView.as_view(), name='category-add'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('category/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-edit'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),  # URL for category detail
]
