"""
URL configuration for fco project.

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
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Fish Chain API is running'})

def redirectRouter(request):
    return redirect('api/docs/')

urlpatterns = [
    path('', redirectRouter),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('roles/', include('role_managements.urls')),
    path('ships/', include('ships.urls')),
    path('regions/', include('regions.urls')),
    path('health/', health_check, name='health_check'),
    # DRF Spectacular documentation URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]