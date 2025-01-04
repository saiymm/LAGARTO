from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),  # List all products
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
