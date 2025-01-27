from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import *

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

# Custom Login Form
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomUserChangeForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, label="Profile Picture")  # Add profile_picture field

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # User fields

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save profile picture to the Customer model
            customer, created = Customer.objects.get_or_create(user=user)
            customer.profile_picture = self.cleaned_data.get('profile_picture')
            customer.save()
        return user
    # Exclude password field from the form
    password = None  # Exclude the password field from the form

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name', 
            'street_address', 
            'city', 
            'state', 
            'postal_code', 
            'country', 
            'phone_number', 
            'is_default'
        ]
        widgets = {
            'street_address': forms.Textarea(attrs={'rows': 3}),
            'phone_number': forms.TextInput(attrs={'maxlength': 15}),
        }
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # You can add validation for phone number format here if needed
        return phone_number

    def save(self, commit=True):
        address = super().save(commit=False)
        # Additional logic can be added here, like setting the default address for the user
        if address.is_default:
            # Make sure only one default address exists per user
            Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
        if commit:
            address.save()
        return address
    
class StarRatingWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        # Handle case where 'value' is None (i.e., no rating selected yet)
        value = value or 0  # Default to 0 if value is None
        stars = ""
        for i in range(1, 6):  # 5 stars
            checked = "checked" if i <= value else ""
            stars += f'<label for="{name}_{i}" class="star {checked}" data-value="{i}">&#9733;</label>'
        return f'<div class="star-rating">{stars}</div>'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': StarRatingWidget(),
            'comment': forms.Textarea(attrs={
                'maxlength': 500,  # Limit comment to 500 characters
                'rows': 3,         # Smaller height (3 rows)
                'cols': 30,        # Smaller width (30 columns)
                'style': 'resize: none;',  # Optional: Disable resizing the textarea
                'placeholder': 'Write your review here...'  # Placeholder text
            }),
        }


    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('Please write a comment.')
        return comment

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise forms.ValidationError('Please select a rating.')
        return rating