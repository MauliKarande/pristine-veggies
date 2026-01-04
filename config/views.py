from django.contrib.auth.models import User

def create_admin_once(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="123"
        )
    return HttpResponse("Admin created")
