from django.shortcuts import render
from orders.models import Order   # adjust import if needed
from accounts.models import Customer
from django.contrib import messages
from accounts.models import Farmer
from django.shortcuts import redirect, get_object_or_404
from orders.models import Order
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order, OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from products.models import Product
from accounts.models import Admin
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Admin

def admin_dashboard(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_login')

    admin = Admin.objects.get(a_id=admin_id)

    return render(request, 'admin_dashboard.html', {
        'admin_name': admin.a_fullname
    })


def admin_orders(request):
    orders = Order.objects.all().order_by('-ord_date')
    return render(request, 'admin_orders.html', {
        'orders': orders
    })


# -------------------------------
# ADMIN – LIST CUSTOMERS
# -------------------------------
def admin_customers(request):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    customers = Customer.objects.all().order_by('c_id')
    return render(request, 'admin_customers.html', {
        'customers': customers
    })


# -------------------------------
# ADMIN – DELETE CUSTOMER
# -------------------------------
def admin_delete_customer(request, customer_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        Customer.objects.filter(c_id=customer_id).delete()
        messages.success(request, "Customer deleted successfully.")

    return redirect('admin_customers')


# -------------------------------
# ADMIN – EDIT CUSTOMER
# -------------------------------
def admin_edit_customer(request, customer_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    customer = Customer.objects.filter(c_id=customer_id).first()
    if not customer:
        messages.error(request, "Customer not found.")
        return redirect('admin_customers')

    if request.method == 'POST':
        customer.c_fullname = request.POST.get('fullname')
        customer.c_email = request.POST.get('email')
        customer.c_phone = request.POST.get('phone')
        customer.c_gender = request.POST.get('gender')
        customer.c_address = request.POST.get('address')

        new_password = request.POST.get('password')
        if new_password:
            customer.c_password = new_password

        customer.save()
        messages.success(request, "Customer updated successfully.")
        return redirect('admin_customers')

    return render(request, 'admin_edit_customer.html', {
        'customer': customer
    })

# -------------------------------
# ADMIN – LIST FARMERS
# -------------------------------
def admin_farmers(request):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    farmers = Farmer.objects.all().order_by('f_id')
    return render(request, 'admin_farmers.html', {
        'farmers': farmers
    })


# -------------------------------
# ADMIN – EDIT FARMER
# -------------------------------
def admin_edit_farmer(request, farmer_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    farmer = Farmer.objects.filter(f_id=farmer_id).first()
    if not farmer:
        messages.error(request, "Farmer not found.")
        return redirect('admin_farmers')

    if request.method == 'POST':
        farmer.f_fullname = request.POST.get('fullname')
        farmer.f_email = request.POST.get('email')
        farmer.f_phone = request.POST.get('phone')
        farmer.f_gender = request.POST.get('gender')
        farmer.f_address = request.POST.get('address')

        new_password = request.POST.get('password')
        if new_password:
            farmer.f_password = new_password

        farmer.save()
        messages.success(request, "Farmer updated successfully.")
        return redirect('admin_farmers')

    return render(request, 'admin_edit_farmer.html', {
        'farmer': farmer
    })


# -------------------------------
# ADMIN – DELETE FARMER
# -------------------------------
def admin_delete_farmer(request, farmer_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        Farmer.objects.filter(f_id=farmer_id).delete()
        messages.success(request, "Farmer deleted successfully.")

    return redirect('admin_farmers')

def admin_delete_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, ord_id=order_id)
        order.delete()
        messages.success(request, f"Order #{order_id} deleted successfully.")
    return redirect('admin_orders')    


def admin_orders(request):
    orders = Order.objects.all().order_by('-ord_date')

    for order in orders:
        items = OrderItem.objects.filter(ord_id=order)

        statuses = list(items.values_list('item_status', flat=True))

        if not statuses:
            order.display_status = 'Pending'

        elif all(s == 'ACCEPTED' for s in statuses):
            order.display_status = 'Accepted'

        elif all(s == 'REJECTED' for s in statuses):
            order.display_status = 'Rejected'

        elif 'ACCEPTED' in statuses and 'REJECTED' in statuses:
            order.display_status = 'Partially Accepted'

        elif 'ACCEPTED' in statuses and 'PENDING' in statuses:
            order.display_status = 'Partially Accepted'

        elif 'REJECTED' in statuses and 'PENDING' in statuses:
            order.display_status = 'Partially Rejected'

        else:
            order.display_status = 'Pending'

    return render(request, 'admin_orders.html', {
        'orders': orders
    })


# ======================================================
# ADMIN – PRODUCT MANAGEMENT (SAFE ADDITION)
# ======================================================

def admin_products(request):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    query = request.GET.get('q')

    products = Product.objects.select_related('f_id').all()

    if query:
        products = products.filter(
            Q(pr_name__icontains=query) |
            Q(pr_category__icontains=query) |
            Q(f_id__f_fullname__icontains=query)
        )

    return render(request, 'admin_products.html', {
        'products': products,
        'query': query
    })


def admin_update_product_status(request, product_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    product = get_object_or_404(Product, pr_id=product_id)

    if request.method == 'POST':
        product.pr_status = request.POST.get('status')
        product.save()
        messages.success(request, "Product status updated successfully.")

    return redirect('admin_products')


def admin_delete_product(request, product_id):
    if request.session.get('user_type') != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        product = get_object_or_404(Product, pr_id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully.")

    return redirect('admin_products')
    
    #admin register

def admin_register(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        login_name = request.POST.get('login_name', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()

        # 🔒 EMPTY FIELD CHECK
        if not fullname or not login_name or not password:
            messages.error(request, "All required fields must be filled")
            return redirect('admin_register')

        if Admin.objects.filter(a_login_name=login_name).exists():
            messages.error(request, "Admin login name already exists")
            return redirect('admin_register')

        Admin.objects.create(
            a_fullname=fullname,
            a_login_name=login_name,
            a_password=password,
            a_email=email,
            a_phone=phone,
            a_gender=gender,
            a_address=address
        )

        messages.success(request, "New admin registered successfully")
        return redirect('admin_dashboard')

    return render(request, 'admin_register.html')
