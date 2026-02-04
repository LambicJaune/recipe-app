"""
Main URL configuration for recipe_project project.

Includes:
- Admin URLs
- Recipe app URLs
- User authentication URLs (signup, login, logout)
- Static / Media file serving in development
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, logout_view, signup_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
    path("signup/", signup_view, name="signup"),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
