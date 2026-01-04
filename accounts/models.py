from django.db import models


class Admin(models.Model):
    a_id = models.AutoField(primary_key=True)
    a_fullname = models.CharField(max_length=100)
    a_login_name = models.CharField(max_length=50)
    a_password = models.CharField(max_length=255)
    a_email = models.EmailField(max_length=100)
    a_phone = models.CharField(max_length=15)
    a_gender = models.CharField(max_length=10)
    a_address = models.TextField()

    def __str__(self):
        return self.a_fullname


class Customer(models.Model):
    c_id = models.AutoField(primary_key=True)
    c_fullname = models.CharField(max_length=100)
    c_login_name = models.CharField(max_length=50)
    c_password = models.CharField(max_length=255)
    c_email = models.EmailField(max_length=100)
    c_phone = models.CharField(max_length=15)
    c_gender = models.CharField(max_length=10)
    c_address = models.TextField()


#✅ NEW FIELD
    profile_image = models.ImageField(
        upload_to='profiles/customers/',
        null=True,
        blank=True
    )    

    def __str__(self):
        return self.c_fullname


class Farmer(models.Model):
    f_id = models.AutoField(primary_key=True)
    f_fullname = models.CharField(max_length=100)
    f_login_name = models.CharField(max_length=50)
    f_password = models.CharField(max_length=255)
    f_email = models.EmailField(max_length=100)
    f_phone = models.CharField(max_length=15)
    f_gender = models.CharField(max_length=10)
    f_address = models.TextField()

    profile_image = models.ImageField(
    upload_to='profiles/farmers/',
    null=True,
    blank=True
)


    def __str__(self):
        return self.f_fullname
