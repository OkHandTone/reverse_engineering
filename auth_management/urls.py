from django.urls import re_path

from . import views

urlpatterns = [
    re_path('login/', views.login_api_view, name='login'),
    re_path('register/', views.register_view, name='register'),
    re_path('profile/', views.my_profile_view, name='my_profile'),
]
