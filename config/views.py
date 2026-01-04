from django.shortcuts import render, redirect
from products.models import Product
from accounts.models import Customer
from accounts.models import Customer
from django.db.models import Q
from products.models import Product


def home(request):
    query = request.GET.get('q')

    products = Product.objects.filter(pr_status='AVAILABLE')

    if query:
        products = products.filter(
            Q(pr_name__icontains=query) |
            Q(pr_category__icontains=query) |
            Q(f_id__f_fullname__icontains=query)
        )

    customer_name = request.session.get('customer_name')

    customer = None
    if request.session.get('customer_id'):
        from accounts.models import Customer
        customer = Customer.objects.get(c_id=request.session.get('customer_id'))

    return render(request, 'index.html', {
        'products': products,
        'customer_name': customer_name,
        'customer': customer,
        'query': query
    })


    
def customer_login(request):
    error = None

    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(
                c_login_name=login_name,
                c_password=password
            )
            # login success
            request.session['customer_id'] = customer.c_id
            request.session['customer_name'] = customer.c_fullname
            return redirect('home')

        except Customer.DoesNotExist:
            error = "Invalid login credentials"

    return render(request, 'login.html', {'error': error})
def customer_logout(request):
    request.session.flush()
    return redirect('home')

