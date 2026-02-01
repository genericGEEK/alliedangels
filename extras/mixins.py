from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


class NextUrlMixin:
    """
    Provides safe handling of ?next= URLs for redirects and cancel links.

    Usage:
    - Add to CBV inheritance
    - Define `default_success_url_name` OR override `get_default_success_url()`
    """

    default_success_url_name = None  # e.g. "event_manage_list"

    def get_next_url(self):
        return self.request.POST.get("next") or self.request.GET.get("next")

    def is_safe_next_url(self, url):
        return url and url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

    def get_default_success_url(self):
        if self.default_success_url_name:
            return reverse(self.default_success_url_name)
        raise NotImplementedError(
            "NextUrlMixin requires either default_success_url_name "
            "or get_default_success_url() to be implemented."
        )

    def get_success_url(self):
        next_url = self.get_next_url()
        if self.is_safe_next_url(next_url):
            return next_url
        return self.get_default_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.get_next_url()
        context["cancel_url"] = (
            context["next"]
            if self.is_safe_next_url(context.get("next"))
            else self.get_default_success_url()
        )
        return context


class PageMetaMixin:
    page_title = None
    is_current = None
    breadcrumbs = None

    def get_page_title(self):
        return self.page_title

    def get_is_current(self):
        return self.is_current

    def get_breadcrumbs(self):
        """
                Priority:
                1) Explicit breadcrumbs defined on the view (class attr)
                2) Breadcrumbs returned by override method
                3) Default: Home > page_title
                """
        if self.breadcrumbs is not None:
            return self.breadcrumbs

        title = self.get_page_title()
        if title:
            return [{"label": title, "url": None}]

        return []

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.get_page_title()
        ctx["is_current"] = self.get_is_current()
        ctx["breadcrumbs"] = self.get_breadcrumbs()
        return ctx
