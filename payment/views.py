from django.shortcuts import render, redirect
from django.contrib import messages

from payment.models import Payment


# --------------------------------
# ADMIN – VIEW ALL PAYMENTS
# --------------------------------
def admin_payments(request):
    admin_id = request.session.get('admin_id')

    # 🔐 ADMIN AUTH CHECK
    if not admin_id:
        messages.error(request, "Please login as admin.")
        return redirect('admin_dashboard')

    # ✅ FIX: order by primary key instead of non-existing field
    payments = Payment.objects.select_related('ord_id').order_by('-p_id')

    return render(request, 'admin_payments.html', {
        'payments': payments
    })

from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
import razorpay

from orders.models import Order
from payment.models import Payment


def confirm_payment(request, order_id):
    order = get_object_or_404(Order, ord_id=order_id)
    payment = get_object_or_404(Payment, ord_id=order)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Fetch payments for Razorpay order
    payments = client.order.fetch_payments(payment.razorpay_order_id)

    if payments["count"] > 0:
        razorpay_payment = payments["items"][0]

        if razorpay_payment["status"] == "captured":
            # Update payment
            payment.p_status = "SUCCESS"
            payment.razorpay_payment_id = razorpay_payment["id"]
            payment.save()

            # Update order
            order.ord_status = "PAID"
            order.ord_payment_at = timezone.now()
            order.save()

            messages.success(request, "Payment successful!")
            return redirect("orders:order_success", order_id=order.ord_id)

    messages.error(request, "Payment not completed yet. Please wait.")
    return redirect("orders:payment_page", order_id=order.ord_id)
