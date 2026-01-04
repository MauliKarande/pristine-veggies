from django.urls import path
from . import views

urlpatterns = [
    path('farmer/product/update/<int:product_id>/', views.update_product, name='update_product'),
    path('farmer/product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
]
