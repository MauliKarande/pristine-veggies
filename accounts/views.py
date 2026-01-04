from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages

from accounts.models import Admin, Farmer, Customer


# =====================================================
# 🔧 HELPER: CLEAR ALL DJANGO MESSAGES
# =====================================================
def clear_messages(request):
    """
    Ensure no old messages leak to next page (especially login).
    """
    storage = get_messages(request)
    for _ in storage:
        pass


# -------------------------------
# CUSTOMER REGISTRATION
# -------------------------------
def customer_register(request):
    error = None

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        login_name = request.POST.get('login_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')

        if Customer.objects.filter(c_login_name=login_name).exists():
            error = "Login name already exists"
        else:
            Customer.objects.create(
                c_fullname=fullname,
                c_login_name=login_name,
                c_password=password,
                c_email=email,
                c_phone=phone,
                c_gender=gender,
                c_address=address
            )
            return redirect('login')

    return render(request, 'register_customer.html', {'error': error})


# -------------------------------
# FARMER REGISTRATION
# -------------------------------
def farmer_register(request):
    error = None

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        login_name = request.POST.get('login_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')

        if Farmer.objects.filter(f_login_name=login_name).exists():
            error = "Login name already exists"
        else:
            Farmer.objects.create(
                f_fullname=fullname,
                f_login_name=login_name,
                f_password=password,
                f_email=email,
                f_phone=phone,
                f_gender=gender,
                f_address=address
            )
            return redirect('login')

    return render(request, 'register_farmer.html', {'error': error})


# -------------------------------
# FARMER LOGIN
# -------------------------------
def farmer_login(request):
    error = None

    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        password = request.POST.get('password')

        try:
            farmer = Farmer.objects.get(
                f_login_name=login_name,
                f_password=password
            )
            request.session.flush()
            clear_messages(request)

            request.session['farmer_id'] = farmer.f_id
            request.session['farmer_name'] = farmer.f_fullname
            request.session['user_type'] = 'FARMER'
            return redirect('farmer_dashboard')

        except Farmer.DoesNotExist:
            error = "Invalid login credentials"

    return render(request, 'farmer_login.html', {'error': error})


# -------------------------------
# FARMER LOGOUT
# -------------------------------
def farmer_logout(request):
    request.session.flush()
    clear_messages(request)
    return redirect('login')


# -------------------------------
# FARMER DASHBOARD
# -------------------------------
def farmer_dashboard(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('login')

    farmer = Farmer.objects.get(f_id=farmer_id)

    return render(request, 'farmer_dashboard.html', {
        'farmer_name': farmer.f_fullname,
        'farmer': farmer
    })


# =====================================================
# CUSTOMER PROFILE
# =====================================================
def customer_profile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(c_id=customer_id)

    if request.method == 'POST':
        customer.c_fullname = request.POST.get('fullname')
        customer.c_email = request.POST.get('email')
        customer.c_phone = request.POST.get('phone')
        customer.c_gender = request.POST.get('gender')
        customer.c_address = request.POST.get('address')

        if 'profile_image' in request.FILES:
            customer.profile_image = request.FILES['profile_image']

        customer.save()
        messages.success(request, "Profile updated successfully")
        return redirect('customer_profile')

    return render(request, 'customer_profile.html', {
        'customer': customer
    })


# =====================================================
# FARMER PROFILE
# =====================================================
def farmer_profile(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('login')

    farmer = Farmer.objects.get(f_id=farmer_id)

    if request.method == 'POST':
        farmer.f_fullname = request.POST.get('fullname')
        farmer.f_email = request.POST.get('email')
        farmer.f_phone = request.POST.get('phone')
        farmer.f_gender = request.POST.get('gender')
        farmer.f_address = request.POST.get('address')

        if 'profile_image' in request.FILES:
            farmer.profile_image = request.FILES['profile_image']

        farmer.save()
        messages.success(request, "Profile updated successfully")
        return redirect('farmer_profile')

    return render(request, 'farmer_profile.html', {
        'farmer': farmer
    })


# -------------------------------
# UNIFIED LOGIN (ADMIN / FARMER / CUSTOMER)
# -------------------------------
def unified_login(request):
    clear_messages(request)  # 🔒 prevent leaked success messages

    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        password = request.POST.get('password')

        # ---- ADMIN ----
        admin = Admin.objects.filter(
            a_login_name=login_name,
            a_password=password
        ).first()
        if admin:
            request.session.flush()
            clear_messages(request)

            request.session['admin_id'] = admin.a_id
            request.session['admin_name'] = admin.a_fullname
            request.session['user_type'] = 'ADMIN'
            return redirect('admin_dashboard')

        # ---- FARMER ----
        farmer = Farmer.objects.filter(
            f_login_name=login_name,
            f_password=password
        ).first()
        if farmer:
            request.session.flush()
            clear_messages(request)

            request.session['farmer_id'] = farmer.f_id
            request.session['farmer_name'] = farmer.f_fullname
            request.session['user_type'] = 'FARMER'
            return redirect('farmer_dashboard')

        # ---- CUSTOMER ----
        customer = Customer.objects.filter(
            c_login_name=login_name,
            c_password=password
        ).first()
        if customer:
            request.session.flush()
            clear_messages(request)

            request.session['customer_id'] = customer.c_id
            request.session['customer_name'] = customer.c_fullname
            request.session['user_type'] = 'CUSTOMER'
            return redirect('home')

        messages.error(request, "Invalid login credentials")

    return render(request, 'unified_login.html')


# -------------------------------
# COMMON LOGOUT (ALL ROLES)
# -------------------------------
def logout_view(request):
    request.session.flush()
    clear_messages(request)
    return redirect('login')


# -------------------------------
# DELETE CUSTOMER PROFILE
# -------------------------------
def delete_customer_profile(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    if request.method == 'POST':
        Customer.objects.filter(c_id=customer_id).delete()
        request.session.flush()
        clear_messages(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')

    return redirect('customer_profile')


# -------------------------------
# DELETE FARMER PROFILE
# -------------------------------
def delete_farmer_profile(request):
    farmer_id = request.session.get('farmer_id')
    if not farmer_id:
        return redirect('login')

    if request.method == 'POST':
        Farmer.objects.filter(f_id=farmer_id).delete()
        request.session.flush()
        clear_messages(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')

    return redirect('farmer_profile')
