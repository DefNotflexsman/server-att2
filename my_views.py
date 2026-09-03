from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

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
    return render(request, 'admin_dashboard.html', context)