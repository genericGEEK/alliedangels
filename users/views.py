from django.contrib import messages
from django.contrib.auth.views import LoginView, auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View

from extras.mixins import PageMetaMixin
from .forms import SiteAuthenticationForm


class SiteLoginView(PageMetaMixin, LoginView):
    template_name = "users/login.html"
    authentication_form = SiteAuthenticationForm
    redirect_authenticated_user = True
    page_title = 'Login'

    def get_success_url(self):
        user = self.request.user

        # Admins go to the staff area
        if user.is_staff:
            return reverse_lazy("connect_inbox")

        # Members later (create this route when ready)
        # For now, you can send non-staff back to home
        return reverse_lazy("home")


class SiteLogoutView(View):
    def get(self, request):
        auth_logout(request)
        messages.info(request, f"You have successfully logged out.")

        response = HttpResponseRedirect(reverse_lazy("home"))
        response.delete_cookie('session_key')
        return response
