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

# Order views (GLOBAL exposure)
from orders import views as order_views


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

    # ✅ FIX: FARMER ORDERS (GLOBAL)
    path('farmer/orders/', order_views.farmer_orders, name='farmer_orders'),
    path('farmer/orders/history/', order_views.farmer_order_history, name='farmer_order_history'),

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
    # CART & CUSTOMER ORDERS
    # =====================
    path('cart/', order_views.view_cart, name='view_cart'),
    path('cart/increase/<int:item_id>/', order_views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', order_views.decrease_quantity, name='decrease_quantity'),
    path('cart/update/<int:item_id>/', order_views.update_quantity, name='update_quantity'),

    path('place-order/', order_views.place_order, name='place_order'),
    path('my-orders/', order_views.my_orders, name='my_orders'),
    path('orders/details/<int:order_id>/', order_views.order_details, name='order_details'),
    path("create-admin/", create_admin_once),


    # =====================
    # ORDERS / PAYMENT (APP URLS)
    # =====================
    path('', include('orders.urls')),
]

# =====================
# MEDIA FILES
# =====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
