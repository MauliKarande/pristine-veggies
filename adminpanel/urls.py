from django.urls import path
from . import views
from payment import views as payment_views   # ✅ NEW IMPORT (SAFE)

urlpatterns = [
    # =====================
    # DASHBOARD
    # =====================
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # =====================
    # ORDERS
    # =====================
    path('orders/', views.admin_orders, name='admin_orders'),
    path('orders/delete/<int:order_id>/', views.admin_delete_order, name='admin_delete_order'),

    # =====================
    # CUSTOMERS
    # =====================
    path('customers/', views.admin_customers, name='admin_customers'),
    path('customers/delete/<int:customer_id>/', views.admin_delete_customer, name='admin_delete_customer'),
    path('customers/edit/<int:customer_id>/', views.admin_edit_customer, name='admin_edit_customer'),

    # =====================
    # FARMERS
    # =====================
    path('farmers/', views.admin_farmers, name='admin_farmers'),
    path('farmers/edit/<int:farmer_id>/', views.admin_edit_farmer, name='admin_edit_farmer'),
    path('farmers/delete/<int:farmer_id>/', views.admin_delete_farmer, name='admin_delete_farmer'),

    # =====================
    # PRODUCTS
    # =====================
    path('products/', views.admin_products, name='admin_products'),
    path('products/update/<int:product_id>/', views.admin_update_product_status, name='admin_update_product_status'),
    path('products/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),

    # =====================
    # PAYMENTS (✅ NEW – ADMIN)
    # =====================
    path('payments/', payment_views.admin_payments, name='admin_payments'),

    ##Admin Panel 

    path('register-admin/', views.admin_register, name='admin_register'),

]
