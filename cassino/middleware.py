from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        public_urls = [
            '/',
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
        
        # Ensure user is properly loaded
        if not hasattr(request, 'user') or request.user.is_anonymous:
            request.user = get_user(request)
        
        # Debug logging
        logger.info(f"Path: {current_path}, Is Public: {is_public}, Is Authenticated: {request.user.is_authenticated}, User: {request.user}")
        
        # If not public and user is not authenticated, redirect to login
        if not is_public and not request.user.is_authenticated:
            logger.info(f"Redirecting {current_path} to login")
            return redirect('usuarios:login')
        
        # If user is authenticated and trying to access login page, redirect to home
        if request.user.is_authenticated and current_path == '/usuarios/login/':
            logger.info(f"Authenticated user accessing login, redirecting to home")
            return redirect('/')
        
        response = self.get_response(request)
        return response 