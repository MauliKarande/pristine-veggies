from django.db import models
from orders.models import Order


class Delivery(models.Model):
    d_id = models.AutoField(primary_key=True)
    d_status = models.CharField(max_length=20)
    d_date = models.DateField()

    ord_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.d_id)
