from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SiteAuthenticationForm(AuthenticationForm):
    """
    Adds CSS classes + placeholders to the default Django login form.
    Field name stays 'username' so LoginView works normally.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        # Username or email field
        self.fields["username"].widget.attrs.update({
            "class": "form-one__control__input",
            "placeholder": "Email or username",
            "autocomplete": "username",
        })

        # Password field
        self.fields["password"].widget.attrs.update({
            "class": "form-one__control__input",
            "placeholder": "Password",
            "autocomplete": "current-password",
        })
