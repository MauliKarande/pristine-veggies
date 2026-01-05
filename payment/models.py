from django.db import models
from orders.models import Order


class Payment(models.Model):
    p_id = models.AutoField(primary_key=True)

    # Existing fields
    p_invoice_no = models.CharField(max_length=50)
    p_method = models.CharField(max_length=30)
    p_status = models.CharField(max_length=20)
    p_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    razorpay_qr_id = models.CharField(max_length=100, null=True, blank=True)

    ord_id = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.p_invoice_no
