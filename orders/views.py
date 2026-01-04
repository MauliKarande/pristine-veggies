from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.contrib import messages
from datetime import datetime   # ✅ PAYMENT ADDITION

from accounts.models import Customer
from products.models import Product
from .models import Order, OrderItem
from payment.models import Payment   # ✅ PAYMENT ADDITION
from django.contrib.messages import get_messages

def clear_messages(request):
    storage = get_messages(request)
    for _ in storage:
        pass



# --------------------------------
# ADD PRODUCT TO CART (SECURE)
# --------------------------------
def add_to_order(request, product_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = get_object_or_404(Customer, c_id=customer_id)
    product = get_object_or_404(Product, pr_id=product_id)

    # 🔐 BACKEND SAFETY
    if product.pr_stock_qty <= 0 or product.pr_status.lower() != 'available':
        messages.error(
            request,
            f'Product "{product.pr_name}" is not available for ordering.'
        )
        return redirect('home')

    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1

    if qty <= 0:
        messages.error(request, "Invalid quantity.")
        return redirect('home')

    if qty > product.pr_stock_qty:
        messages.error(
            request,
            f'Only {product.pr_stock_qty} Kg available for "{product.pr_name}".'
        )
        return redirect('home')

    order, created = Order.objects.get_or_create(
        c_id=customer,
        ord_status='CART',
        defaults={
            'ord_date': timezone.now().date(),
            'ord_total_amount': 0,
            'ord_delivery_required': 'YES'
        }
    )

    order_item, item_created = OrderItem.objects.get_or_create(
        ord_id=order,
        pr_id=product,
        defaults={
            'item_quantity': qty,
            'item_price': product.pr_price_per_kg
        }
    )

    if not item_created:
        if order_item.item_quantity + qty > product.pr_stock_qty:
            messages.error(
                request,
                f'Only {product.pr_stock_qty} Kg available for "{product.pr_name}".'
            )
            return redirect('view_cart')

        order_item.item_quantity += qty
        order_item.save()

    recalculate_total(order)

    messages.success(
        request,
      #  f'Added {qty} Kg of "{product.pr_name}" to cart.'
    )

    return redirect('home')


# --------------------------------
# VIEW CART
# --------------------------------
def view_cart(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    try:
        order = Order.objects.get(c_id=customer_id, ord_status='CART')
        items = OrderItem.objects.filter(ord_id=order)
    except Order.DoesNotExist:
        order = None
        items = []

    return render(request, 'cart.html', {
        'order': order,
        'items': items
    })


# --------------------------------
# UPDATE QUANTITIES
# --------------------------------
def increase_quantity(request, item_id):
    item = get_object_or_404(OrderItem, item_id=item_id)
    product = item.pr_id

    if item.item_quantity + 1 > product.pr_stock_qty:
        messages.error(
            request,
            f'Only {product.pr_stock_qty} Kg available for "{product.pr_name}".'
        )
        return redirect('view_cart')

    item.item_quantity += 1
    item.save()
    recalculate_total(item.ord_id)

    return redirect('view_cart')


def decrease_quantity(request, item_id):
    item = get_object_or_404(OrderItem, item_id=item_id)

    if item.item_quantity > 1:
        item.item_quantity -= 1
        item.save()
        recalculate_total(item.ord_id)
    else:
        order = item.ord_id
        item.delete()
        recalculate_total(order)

    return redirect('view_cart')


def update_quantity(request, item_id):
    if request.method == 'POST':
        qty = int(request.POST.get('quantity'))
        item = get_object_or_404(OrderItem, item_id=item_id)
        product = item.pr_id

        if qty <= 0:
            order = item.ord_id
            item.delete()
            recalculate_total(order)
        elif qty > product.pr_stock_qty:
            messages.error(
                request,
                f'Only {product.pr_stock_qty} Kg available for "{product.pr_name}".'
            )
        else:
            item.item_quantity = qty
            item.save()
            recalculate_total(item.ord_id)

    return redirect('view_cart')


# --------------------------------
# PLACE ORDER (🔥 STOCK REDUCTION HERE)
# --------------------------------
def place_order(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    order = get_object_or_404(Order, c_id=customer_id, ord_status='CART')
    items = OrderItem.objects.filter(ord_id=order)

    # 🔥 REDUCE STOCK
    for item in items:
        product = item.pr_id
        product.pr_stock_qty -= item.item_quantity

        if product.pr_stock_qty <= 0:
            product.pr_stock_qty = 0
            product.pr_status = 'OUT_OF_STOCK'

        product.save()

    # FINALIZE ORDER
    order.ord_status = 'PLACED'
    order.ord_date = timezone.now().date()
    order.save()

   # messages.success(request, "Order placed successfully!")
    return redirect('orders:payment_page', order_id=order.ord_id)

    # ✅ PAYMENT FLOW CHANGE
    return redirect('orders:payment_page', order_id=order.ord_id)



# --------------------------------
# MY ORDERS
# --------------------------------
def my_orders(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    orders = Order.objects.filter(
        c_id=customer_id
    ).exclude(ord_status='CART').order_by('-ord_date')

    for order in orders:
        items = order.orderitem_set.all()
        statuses = [item.item_status for item in items]

        if all(s == 'PLACED' for s in statuses):
            order.display_status = 'Pending'
        elif all(s == 'ACCEPTED' for s in statuses):
            order.display_status = 'Accepted'
        elif all(s == 'REJECTED' for s in statuses):
            order.display_status = 'Rejected'
        elif 'REJECTED' in statuses:
            order.display_status = 'Partially Rejected'
        else:
            order.display_status = 'Partially Accepted'

    return render(request, 'my_orders.html', {
        'orders': orders
    })


# --------------------------------
# TOTAL CALCULATION
# --------------------------------
def recalculate_total(order):
    total = 0
    items = OrderItem.objects.filter(ord_id=order)

    for item in items:
        total += item.item_quantity * item.item_price

    order.ord_total_amount = total
    order.save()


def farmer_orders(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    orders = Order.objects.filter(
        orderitem__pr_id__f_id=farmer_id,
        orderitem__item_status='PLACED'
    ).distinct().order_by('-ord_date')

    return render(request, 'farmer_orders.html', {
        'orders': orders
    })


def accept_order(request, order_id):
    farmer_id = request.session.get('farmer_id')

    OrderItem.objects.filter(
        ord_id=order_id,
        pr_id__f_id=farmer_id,
        item_status='PLACED'
    ).update(item_status='ACCEPTED')

    return redirect('farmer_order_history')


def reject_order(request, order_id):
    farmer_id = request.session.get('farmer_id')

    OrderItem.objects.filter(
        ord_id=order_id,
        pr_id__f_id=farmer_id,
        item_status='PLACED'
    ).update(item_status='REJECTED')

    return redirect('farmer_order_history')


def farmer_order_history(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('farmer_login')

    orders = Order.objects.filter(
        orderitem__pr_id__f_id=farmer_id
    ).distinct().order_by('-ord_date')

    return render(request, 'farmer_order_history.html', {
        'orders': orders
    })


def order_details(request, order_id):
    order = get_object_or_404(Order, ord_id=order_id)
    items = OrderItem.objects.filter(ord_id=order)

    customer_id = request.session.get('customer_id')
    farmer_id = request.session.get('farmer_id')

    if customer_id:
        if order.c_id.c_id != customer_id:
            messages.error(request, "You are not authorized to view this order.")
            return redirect('my_orders')

        visible_items = items

    elif farmer_id:
        visible_items = items.filter(pr_id__f_id=farmer_id)

        if not visible_items.exists():
            messages.error(request, "You are not authorized to view this order.")
            return redirect('farmer_orders')
    else:
        return redirect('home')

    return render(request, 'order_details.html', {
        'order': order,
        'items': visible_items
    })


def admin_orders(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    orders = Order.objects.exclude(ord_status='CART').order_by('-ord_date')

    for order in orders:
        items = order.orderitem_set.all()
        statuses = [item.item_status for item in items]

        if all(s == 'PLACED' for s in statuses):
            order.display_status = 'Pending'
        elif all(s == 'ACCEPTED' for s in statuses):
            order.display_status = 'Accepted'
        elif all(s == 'REJECTED' for s in statuses):
            order.display_status = 'Rejected'
        elif 'REJECTED' in statuses:
            order.display_status = 'Partially Rejected'
        else:
            order.display_status = 'Partially Accepted'

    return render(request, 'admin_orders.html', {
        'orders': orders
    })


# --------------------------------
# PAYMENT PAGE (✅ NEW)
# --------------------------------
def payment_page(request, order_id):
    order = get_object_or_404(Order, ord_id=order_id)
    return render(request, 'payment.html', {
        'order': order
    })


# --------------------------------
# CONFIRM PAYMENT (✅ NEW)
# --------------------------------
def confirm_payment(request, order_id):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '').strip()

        order = get_object_or_404(Order, ord_id=order_id)

        # ✅ FIX: invoice number must NEVER be NULL
        if transaction_id:
            invoice_no = transaction_id
        else:
            invoice_no = f"INV-ORD-{order.ord_id}"

        Payment.objects.create(
            ord_id=order,
            p_amount=order.ord_total_amount,
            p_method=payment_method,
            p_status='SUCCESS',
            p_invoice_no=invoice_no
        )

        clear_messages(request)
        messages.success(request, "Payment recorded successfully!")

        return redirect('my_orders')