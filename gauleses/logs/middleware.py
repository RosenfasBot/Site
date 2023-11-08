from .models import Log
from django.utils.deprecation import MiddlewareMixin
import json
from django.conf import settings

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.',)


def get_client_ip(request):
    remote_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    ip = remote_address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        while len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX):
            proxies.pop(0)
            if len(proxies) > 0:
                ip = proxies[0]
    return ip


class DebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        safe = False
        userRequest = None
        if request.user.is_authenticated:
            userRequest = request.user
        ipAddress = get_client_ip(request)
        urlString = request.build_absolute_uri()
        requestDaCO = False
        try:
            requestDaCO = userRequest.is_CO
        except:
            pass
        googleBot = True if "(compatible; Googlebot/2.1; +http://www.google.com/bot.html)" in request.META[
            'HTTP_USER_AGENT'] else False
        if not request.get_full_path() in settings.ULTRA_SAFE_PATH and not googleBot:
            if (request.get_full_path() in settings.SAFE_PATH and request.method == 'GET') or requestDaCO:
                safe = True
            requestString = request.method + ' | ' + urlString
            if request.method == 'POST':
                data = request.POST.dict()
                data.pop('csrfmiddlewaretoken', None)
                sen = data.pop('password', None)
                if sen:
                    data['password'] = hash(sen)
                data.pop('g-recaptcha-response', None)
                requestString += ' | ' + str(data)
            Log(user=userRequest, ip=ipAddress, request=requestString, safe=safe).save()
