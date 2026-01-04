from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from accounts.models import Farmer



# -----------------------------
# CUSTOMER HOME (FILTERED)
# -----------------------------
def home(request):
    products = Product.objects.filter(pr_status='AVAILABLE')

    customer_name = request.session.get('customer_name')

    return render(request, 'index.html', {
        'products': products,
        'customer_name': customer_name
    })


# -----------------------------
# FARMER ADD PRODUCT
# -----------------------------
def add_product(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    farmer = get_object_or_404(Farmer, f_id=farmer_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stock_qty = request.POST.get('stock_qty')
        description = request.POST.get('description')

        image = request.FILES.get('image')

        Product.objects.create(
            pr_name=name,
            pr_category=category,
            pr_price_per_kg=price,
            pr_stock_qty=stock_qty,
            pr_status='AVAILABLE',
            pr_description=description,
            pr_image=image,
            f_id=farmer
        )

        messages.success(
            request,
            f'Product "{name}" added successfully!'
        )

        return redirect('farmer_dashboard')

    return render(request, 'add_product.html')


# -----------------------------
# FARMER VIEW PRODUCTS
# -----------------------------
def my_products(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    products = Product.objects.filter(f_id=farmer_id)

    return render(request, 'farmer_products.html', {
        'products': products
    })


# -----------------------------
# FARMER UPDATE PRODUCT
# -----------------------------
def update_product(request, product_id):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    product = get_object_or_404(
        Product,
        pr_id=product_id,
        f_id=farmer_id
    )

    if request.method == 'POST':
        product.pr_stock_qty = request.POST.get('stock_qty')
        product.pr_status = request.POST.get('status')
        product.save()

        messages.success(
            request,
            f'Product "{product.pr_name}" updated successfully!'
        )

    return redirect('farmer_products')

def accept_order(request, order_id):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    order = get_object_or_404(Order, ord_id=order_id, ord_status='PLACED')

    # Verify this order has this farmer's product
    has_farmer_product = OrderItem.objects.filter(
        ord_id=order,
        pr_id__f_id=farmer_id
    ).exists()

    if not has_farmer_product:
        messages.error(request, "You are not authorized to accept this order.")
        return redirect('farmer_orders')

    order.ord_status = 'ACCEPTED'
    order.save()

    messages.success(request, f"Order #{order.ord_id} accepted.")
    return redirect('farmer_orders')


def reject_order(request, order_id):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    order = get_object_or_404(Order, ord_id=order_id, ord_status='PLACED')

    items = OrderItem.objects.filter(
        ord_id=order,
        pr_id__f_id=farmer_id
    )

    if not items.exists():
        messages.error(request, "You are not authorized to reject this order.")
        return redirect('farmer_orders')

    # 🔄 RESTORE STOCK
    for item in items:
        product = item.pr_id
        product.pr_stock_qty += item.item_quantity
        product.pr_status = 'AVAILABLE'
        product.save()

    order.ord_status = 'REJECTED'
    order.save()

    messages.success(request, f"Order #{order.ord_id} rejected and stock restored.")
    return redirect('farmer_orders')


def delete_product(request, product_id):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    product = get_object_or_404(
        Product,
        pr_id=product_id,
        f_id=farmer_id
    )

    product_name = product.pr_name
    product.delete()

    messages.success(
        request,
        f'Product "{product_name}" deleted successfully!'
    )

    return redirect('farmer_products')
