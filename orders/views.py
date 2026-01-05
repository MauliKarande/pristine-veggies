from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.contrib import messages


from accounts.models import Customer
from products.models import Product
from .models import Order, OrderItem
from payment.models import Payment   # ✅ PAYMENT ADDITION
from django.contrib.messages import get_messages
import razorpay
from django.conf import settings


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
        return redirect('login')

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
        f'Added {qty} Kg of "{product.pr_name}" to cart.'
    )

    return redirect('home')


# --------------------------------
# VIEW CART
# --------------------------------
def view_cart(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    try:
        order = Order.objects.get(c_id=customer_id, ord_status='CART')
        items = OrderItem.objects.filter(ord_id=order)
        cart_count = items.count()
    except Order.DoesNotExist:
        order = None
        items = []
        cart_count = 0

    return render(request, 'cart.html', {
        'order': order,
        'items': items,
        'cart_count': cart_count
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
        return redirect('login')

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

        # ✅ IMPORTANT: MARK ITEM AS PLACED
        item.item_status = 'PLACED'
        item.save()

    order.ord_status = 'PLACED'
    order.ord_date = order.ord_created_at.date()
    order.save()

    return redirect('orders:payment_page', order_id=order.ord_id)



# --------------------------------
# MY ORDERS
# --------------------------------
def my_orders(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

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
    orderitem__item_status='PLACED').distinct().order_by('-ord_date')


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

    return redirect('orders:farmer_order_history')


def reject_order(request, order_id):
    farmer_id = request.session.get('farmer_id')

    OrderItem.objects.filter(
        ord_id=order_id,
        pr_id__f_id=farmer_id,
        item_status='PLACED'
    ).update(item_status='REJECTED')

    return redirect('orders:farmer_order_history')


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

    amount_paise = int(order.ord_total_amount * 100)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"ORD-{order.ord_id}",
        "payment_capture": 1
    })

    # Save payment record
    Payment.objects.create(
        ord_id=order,
        p_invoice_no=f"ORD-{order.ord_id}",
        p_method="RAZORPAY",
        p_status="PENDING",
        p_amount=order.ord_total_amount,
        razorpay_order_id=razorpay_order["id"]
    )

    return render(request, "payment.html", {
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount_paise,
    })


from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib


@csrf_exempt
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, ord_id=order_id)

    payment = Payment.objects.filter(
        ord_id=order,
        p_status="PENDING"
    ).last()

    if not payment:
        messages.error(request, "Payment record not found.")
        return redirect('orders:payment_page', order_id=order.ord_id)

    # Razorpay sends POST data
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # 🔐 Signature verification
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        messages.error(request, "Payment verification failed.")
        return redirect('orders:payment_page', order_id=order.ord_id)

    # ✅ Payment verified
    payment.p_status = "SUCCESS"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.save()

    # ✅ Update order
    order.ord_status = "PAID"
    order.ord_payment_at = timezone.now()
    order.save()

    messages.success(request, "Payment successful!")

    return redirect('orders:order_success', order_id=order.ord_id)




# --------------------------------
# CONFIRM PAYMENT (✅ NEW)
# --------------------------------



def order_success(request, order_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    order = get_object_or_404(
        Order,
        ord_id=order_id,
        c_id=customer_id
    )

    # Optional safety: ensure payment is done
    if not order.ord_payment_at:
        messages.error(request, "Payment not completed for this order.")
        return redirect('my_orders')

    return render(request, 'order_success.html', {
        'order': order
    })

from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
import razorpay

from orders.models import Order
from payment.models import Payment






