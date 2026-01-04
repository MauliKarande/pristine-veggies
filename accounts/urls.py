from django.urls import path
from . import views

urlpatterns = [
    # Unified Login (used by Admin / Farmer / Customer)
    path('login/', views.unified_login, name='login'),

    # Customer Registration
    path('register/', views.customer_register, name='customer_register'),


    path('profile/', views.customer_profile, name='customer_profile'),

    path('farmer/profile/', views.farmer_profile, name='farmer_profile'),
    
    path('customer/profile/delete/', views.delete_customer_profile, name='delete_customer_profile'),
    
    
    path('farmer/profile/delete/', views.delete_farmer_profile, name='delete_farmer_profile'),

    
    #farmer registration 

    path('farmer/register/', views.farmer_register, name='farmer_register'),

    # Common Logout (works for all roles)
    path('logout/', views.logout_view, name='logout'),


]
