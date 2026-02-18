from django.urls import path
from .api_views import (
    EntryListAPI,
    EntryDetailAPI,
    EntryCreateAPI,
    # CommentListCreateAPI,
    # ToggleLikeAPI,
)

app_name = 'entrada_api'

urlpatterns = [
    path('entries/', EntryListAPI.as_view()),
    path('entries/<slug:slug>/', EntryDetailAPI.as_view()),
    path('entries/create/', EntryCreateAPI.as_view()),
    # path('entries/<int:entry_id>/comments/', CommentListCreateAPI.as_view()),
    # path('entries/<int:entry_id>/like/', ToggleLikeAPI.as_view()),
]
