from django.db import models
from accounts.models import Customer
from products.models import Product


class Order(models.Model):
    ord_id = models.AutoField(primary_key=True)
    ord_date = models.DateField()
    ord_total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    ord_delivery_required = models.CharField(max_length=10)
    ord_status = models.CharField(max_length=20)

    c_id = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.ord_id)


class OrderItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)

    ord_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    pr_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    item_status = models.CharField(
    max_length=10,
    default='PLACED'
    )


    def __str__(self):
        return str(self.item_id)
