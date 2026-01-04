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
