from django.contrib import auth
from django.contrib.auth.models import User

from msw.forms import AuthenticationForm

def handle_login(request, only_active=True):
    #auth.logout(request)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST, only_active=only_active)
        if form.is_valid():
            auth.login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

        return form

    request.session.set_test_cookie()
    return AuthenticationForm()
