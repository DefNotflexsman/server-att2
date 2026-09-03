from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('/admindashboard/')
            else:
                messages.error(request, "Invalid credentials or unauthorized access.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@staff_member_required
def admin_dashboard(request):
    # Fetch summary metrics or stats to display on the dashboard
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard.html', context)