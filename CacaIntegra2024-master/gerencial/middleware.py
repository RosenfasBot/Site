from django.utils.deprecation import MiddlewareMixin
import json
from django.conf import settings
from .models import WebSiteLock
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.http import Http404
from users.models import User
from django.conf import settings


def check_lock():
    lock = -1
    agora = timezone.now()
    obj = WebSiteLock.objects.exclude(start_time__gte = agora).exclude(end_time__lte = agora)
    for i in obj:
        if i.lock_type>lock:
            lock = i.lock_type
    return lock

def build_user_session():
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    userSessions = []
    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        if not data.get('_password_reset_token', False) and data:
            sId = int(data.get('_auth_user_id', None))
            user = User.objects.get(id=sId)
            userSessions.append({"session":session, "user":user})
    return userSessions

class LockMiddleware(MiddlewareMixin):
    def process_request(self, request):
        lock_status = check_lock()
        if lock_status>=0:
            user_sessions = build_user_session()
            for usSess in user_sessions:
                if usSess['user'].is_CA:
                    usSess['session'].delete()
                if usSess['user'].is_CO and lock_status==1 and not usSess['user'].is_superuser:
                    usSess['session'].delete()
            if not request.user.is_anonymous:
                if request.user.is_CA or (request.user.is_CO and not request.user.is_superuser and lock_status==1):
                    raise Http404()
                