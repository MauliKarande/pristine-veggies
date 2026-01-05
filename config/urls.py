from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

# Home
from .views import home

# Product views
from products.views import add_product, my_products, update_product

# Farmer views
from accounts.views import (
    farmer_login,
    farmer_logout,
    farmer_dashboard,
)

urlpatterns = [
    # =====================
    # DJANGO ADMIN
    # =====================
    path('admin/', admin.site.urls),

    # =====================
    # HOME
    # =====================
    path('', home, name='home'),

    # =====================
    # ACCOUNTS (CUSTOMER)
    # =====================
    path('', include('accounts.urls')),

    # =====================
    # ADMIN PANEL
    # =====================
    path('adminpanel/', include('adminpanel.urls')),

    # =====================
    # FARMER AUTH & DASHBOARD
    # =====================
    path('farmer/login/', farmer_login, name='farmer_login'),
    path('farmer/logout/', farmer_logout, name='farmer_logout'),
    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),

    # =====================
    # FARMER PRODUCTS
    # =====================
    path('farmer/products/', my_products, name='farmer_products'),
    path('farmer/add-product/', add_product, name='add_product'),
    path('farmer/product/update/<int:product_id>/', update_product, name='update_product'),

    # =====================
    # PRODUCTS
    # =====================
    path('', include('products.urls')),

    # =====================
    # ORDERS & PAYMENT (SINGLE SOURCE OF TRUTH ✅)
    # =====================
    path('', include('orders.urls')),
]

# =====================
# MEDIA FILES
# =====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
