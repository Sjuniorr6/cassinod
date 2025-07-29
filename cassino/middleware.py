from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        public_urls = [
            '/landing/',
            '/usuarios/login/',
            '/usuarios/register/',
            '/admin/',
        ]
        
        # Check if the current path is public
        current_path = request.path
        
        # Allow access to static and media files
        if current_path.startswith('/static/') or current_path.startswith('/media/'):
            return self.get_response(request)
        
        # Check if current path is in public URLs
        is_public = any(current_path.startswith(url) for url in public_urls)
        
        # If not public and user is not authenticated, redirect to login
        if not is_public and not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        response = self.get_response(request)
        return response 