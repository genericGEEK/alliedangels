from django.urls import path
from .views import HomePageView, AboutPageView, ProgramPageView, SupportPageView, SupportThanksPageView, SupportCancelPageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('programs/', ProgramPageView.as_view(), name='programs'),
    path('support/', SupportPageView.as_view(), name='support'),
    path('support/thanks/', SupportThanksPageView.as_view(), name='support-thanks'),
    path('support/not-completed/', SupportCancelPageView.as_view(), name='support-cancel'),
]