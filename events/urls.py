from django.urls import path
from .views import (
    EventListView, CategoryListView, CategoryEditView, CategoryDeleteView, CategoryAddView,
EventManageListView, EventManageDetailView, EventManageAddView, EventManageEditView, EventManageDeleteView,
SeriesListView, SeriesView, SeriesEditView, SeriesAddView, SeriesDeleteView, EventView
)


urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),

    # Event Management
    path('manage/', EventManageListView.as_view(), name='event_manage_list'),
    path('manage/add/', EventManageAddView.as_view(), name='event_manage_add'),
    path('manage/categories/', CategoryListView.as_view(), name='category_list'),
    path('manage/categories/add/', CategoryAddView.as_view(), name='category_add'),
    path('manage/categories/<slug:slug>/edit/', CategoryEditView.as_view(), name='category_edit'),
    path('manage/categories/<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('manage/<slug:slug>/edit/', EventManageEditView.as_view(), name='event_manage_edit'),
    path('manage/<slug:slug>/delete/', EventManageDeleteView.as_view(), name='event_manage_delete'),
    path('manage/series/', SeriesListView.as_view(), name='series_list'),
    path('manage/series/add/', SeriesAddView.as_view(), name='series_add'),
    path('manage/series/<slug:slug>/', SeriesView.as_view(), name='series_detail'),
    path('manage/series/<slug:slug>/edit/', SeriesEditView.as_view(), name='series_edit'),
    path('manage/series/<slug:slug>/delete/', SeriesDeleteView.as_view(), name='series_delete'),


    path('<slug:slug>/', EventView.as_view(), name='event_detail'),
    path('manage/<slug:slug>/', EventManageDetailView.as_view(), name='event_manage_detail'),

    # Categories

]
