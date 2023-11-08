from django.shortcuts import render
from .models import Log
from users.views import CA_check, CO_check, IsCOMixin
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(CO_check, login_url='login', redirect_field_name=None)
def view_logs(request):
    logs = Log.objects.filter().order_by('-timestamp')[:1000]
    context = {'logs': logs}
    return render(request, './logs/viewLogs.html', context)
