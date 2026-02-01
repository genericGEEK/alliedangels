from django.urls import path
from .views import ConnectView, ConnectThanksView, InterestSubmissionListView, InterestSubmissionConfirmView, InterestSubmissionDetailView

urlpatterns = [
    path('', ConnectView.as_view(), name="connect"),
    path('thanks/', ConnectThanksView.as_view(), name="connect_thanks"),
    path('inbox/', InterestSubmissionListView.as_view(), name="connect_inbox"),
    path('inbox/<int:pk>/detail/', InterestSubmissionDetailView.as_view(), name="connect_inbox_detail"),
    path('inbox/<int:pk>/contacted/', InterestSubmissionConfirmView.as_view(), name="connect_inbox_contact"),
]
