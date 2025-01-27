from django.shortcuts import redirect
from django.conf import settings
from django.contrib.admin.sites import site
from django.urls import resolve

class RedirectToLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the requested URL is part of the admin panel
        if resolve(request.path).app_name == 'admin':
            # If the user is not a superuser, redirect to the login page
            if not request.user.is_authenticated or not request.user.is_superuser:
                return redirect(settings.LOGIN_URL)
                
        response = self.get_response(request)
        return response
