from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # -----------------------------
    # CUSTOMER CART & ORDER
    # -----------------------------
    path('orders/add/<int:product_id>/', views.add_to_order, name='add_to_order'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/update/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # -----------------------------
    # PAYMENT
    # -----------------------------
    path('orders/payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('orders/payment/confirm/<int:order_id>/', views.confirm_payment, name='confirm_payment'),

    # -----------------------------
    # FARMER ORDERS (🔥 MISSING PART)
    # -----------------------------
    path('farmer/orders/', views.farmer_orders, name='farmer_orders'),
    path('farmer/orders/accept/<int:order_id>/', views.accept_order, name='accept_order'),
    path('farmer/orders/reject/<int:order_id>/', views.reject_order, name='reject_order'),
    path('farmer/orders/history/', views.farmer_order_history, name='farmer_order_history'),

    # -----------------------------
    # ADMIN ORDERS
    # -----------------------------
    path('admin/orders/', views.admin_orders, name='admin_orders'),
]
