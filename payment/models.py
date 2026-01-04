from django.db import models
from orders.models import Order


class Payment(models.Model):
    p_id = models.AutoField(primary_key=True)
    p_invoice_no = models.CharField(max_length=50)
    p_method = models.CharField(max_length=30)
    p_status = models.CharField(max_length=20)
    p_amount = models.DecimalField(max_digits=10, decimal_places=2)

    ord_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.p_invoice_no
