from .models import ActivityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_activity(request, action, target_model, target_id, description):
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        target_model=target_model,
        target_id=target_id,
        description=description,
        ip_address=get_client_ip(request),
    )
