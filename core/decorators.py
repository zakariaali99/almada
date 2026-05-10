import time

from django.core.cache import cache


def rate_limit(key_prefix, max_attempts=50, window_seconds=300):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR", "unknown")
            cache_key = f"{key_prefix}:{ip}"
            now = time.time()
            attempts = cache.get(cache_key, [])
            attempts = [t for t in attempts if now - t < window_seconds]
            if len(attempts) >= max_attempts:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("عدد المحاولات تجاوز الحد المسموح. حاول لاحقاً.")
            attempts.append(now)
            cache.set(cache_key, attempts, window_seconds)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
