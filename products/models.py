from django.db import models
from accounts.models import Farmer


class Product(models.Model):
    pr_id = models.AutoField(primary_key=True)
    pr_name = models.CharField(max_length=100)
    pr_category = models.CharField(max_length=50)
    pr_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    pr_stock_qty = models.IntegerField()
    pr_description = models.TextField()
    pr_status = models.CharField(max_length=20)

    f_id = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE
    )
    pr_image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.pr_name
