from django import forms
from .models import InterestSubmission, InterestTag


class InterestForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=InterestTag.objects.filter(is_active=True).order_by("group", "name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="I'm interested in",
    )

    class Meta:
        model = InterestSubmission
        fields = ["first_name", "last_name", "email", "phone", "interests", "message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Anything you'd like us to know (optional)",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-one__control__input', 'placeholder': 'First Name', 'id': 'first_name', 'name': 'first_name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-one__control__input', 'placeholder': 'Last Name', 'id': 'last_name', 'name': 'last_name'})
        self.fields['email'].widget.attrs.update({'class': 'form-one__control__input', 'placeholder': 'Email Address', 'id': 'email', 'name': 'email'})
        self.fields['phone'].widget.attrs.update({'class': 'form-one__control__input', 'placeholder': 'Phone Number', 'id': 'phone', 'name': 'phone'})
        self.fields['message'].widget.attrs.update({'class': 'form-one__control__input form-one__control__message', 'placeholder': 'Message', 'id': 'message', 'name': 'message'})

    def clean_message(self):
        msg = (self.cleaned_data.get("message") or "").strip()
        return msg
