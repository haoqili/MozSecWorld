from functools import wraps

from django.http import HttpResponseForbidden

from ratelimit.backends.cachebe import CacheBackend


def _method_match(request, method=None):
    if method is None:
        method = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']
    if not isinstance(method, list):
        method = [method]
    return request.method in method


_PERIODS = {
    's': 1,
    'm': 60,
    'h': 60 * 60,
    'd': 24 * 60 * 60,
}


def _split_rate(rate):
    count, period = rate.split('/')
    count = int(count)
    return count, _PERIODS[period.lower()]


_backend = CacheBackend()


def ratelimit(ip=True, block=False, method=None, field=None, rate='5/m'):
    def decorator(fn):
        count, period = _split_rate(rate)
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            if _method_match(request, method):
                _backend.count(request, ip, field, period)
                if _backend.limit(request, ip, field, count):
                    if block:
                        return HttpResponseForbidden()
                    request.limited = True
            return fn(request, *args, **kw)
        return _wrapped
    return decorator
