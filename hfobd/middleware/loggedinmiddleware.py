from django.conf import settings
from django.shortcuts import redirect

class LoggedInMiddleware(object):
    def process_request(self, request):
        if request.path.lower() == '/landing':
            return None
        if not settings.LOGIN_REQUIRED:
            return None
        if request.user.is_authenticated():
            return None
        return redirect('/landing')