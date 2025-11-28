"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf import settings
import os


def serve_react(request):
    """
    Serve React SPA index.html for all non-API routes.
    This allows React Router to handle client-side routing.
    """
    try:
        index_path = os.path.join(settings.BASE_DIR, 'react', 'build', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(
            'React build not found. Please run: cd react && npm install && npm run build',
            status=500,
            content_type='text/plain'
        )
    except Exception as e:
        return HttpResponse(
            f'Error serving React app: {str(e)}',
            status=500,
            content_type='text/plain'
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

# Catch-all route for React SPA - must be last
# This handles all routes like /register, /login, /dashboard etc.
# and allows React Router to handle them on the client side
urlpatterns += [
    re_path(r'^.*$', serve_react, name='spa-fallback'),
]
