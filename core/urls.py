from django.urls import path
from .views import HomePageView, AboutPageView, ProgramPageView, DonatePageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('programs/', ProgramPageView.as_view(), name='programs'),
    path('donate/', DonatePageView.as_view(), name='donate'),
]