from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *

# ListView: Display all products
class ProductListView(ListView):
    model = Product
    template_name = 'app/product_list.html'  # Your template for listing products
    context_object_name = 'products'

# DetailView: Display a specific product's details
class ProductDetailView(DetailView):
    model = Product
    template_name = 'app/product_detail.html'  # Your template for product details
    context_object_name = 'product'

# CreateView: Add a new product
class ProductCreateView(CreateView):
    model = Product
    template_name = 'app/product_form.html'  # Your template for the product form
    fields = ['name', 'description', 'price', 'stock', 'category', 'image']  # Fields to display in the form
    success_url = reverse_lazy('product-list')  # Redirect after successful creation

# UpdateView: Edit an existing product
class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'app/product_form.html'  # Your template for the product form
    fields = ['name', 'description', 'price', 'stock', 'category', 'image']  # Fields to display in the form
    success_url = reverse_lazy('product-list')  # Redirect after successful update

# DeleteView: Delete an existing product
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'app/product_confirm_delete.html'  # Your template for delete confirmation
    success_url = reverse_lazy('product-list')  # Redirect after successful deletion



# CreateView for adding a new category
class CategoryCreateView(CreateView):
    model = Category
    template_name = 'app/category_form.html'  # Template for the category form
    fields = ['name', 'description']  # Fields to display in the form
    success_url = reverse_lazy('category-list')  # Redirect after successful creation

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'app/category_detail.html'  # Template for displaying the category details
    context_object_name = 'category'  # Context variable to use in the template

class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'app/category_form.html'  # Reusing the same template as the create view
    fields = ['name', 'description']  # Fields to display in the form
    success_url = reverse_lazy('category-list')  # Redirect after successful update

class CategoryListView(ListView):
    model = Category
    template_name = 'app/category_list.html'  # Template for displaying categories
    context_object_name = 'categories'  # Context variable to use in the template

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'app/category_confirm_delete.html'  # Template for confirmation before deletion
    success_url = reverse_lazy('category-list')  # Redirect after successful deletion



