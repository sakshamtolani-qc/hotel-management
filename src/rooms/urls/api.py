from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static


app_name = "rooms"

from ..views.api import (
    RoomListView,
    RoomDetailView, 
    RoomCreateView,
    RoomUpdateView,
    RoomDeleteView,
    RoomAvailabilityView,
    AvailableRoomsView,
    RoomStatsView
)

urlpatterns = [
    # Individual API endpoints
    path("", RoomListView.as_view(), name="room-list-base"),
    path("list/", RoomListView.as_view(), name="room-list"),
    path("create/", RoomCreateView.as_view(), name="room-create"),
    path("<int:room_id>/", RoomDetailView.as_view(), name="room-detail-short"),
    path("<int:room_id>/detail/", RoomDetailView.as_view(), name="room-detail"),
    path("<int:room_id>/update/", RoomUpdateView.as_view(), name="room-update"),
    path("<int:room_id>/delete/", RoomDeleteView.as_view(), name="room-delete"),
    
    # Availability and booking features
    path("check-availability/", RoomAvailabilityView.as_view(), name="room-availability"),
    path("available/", AvailableRoomsView.as_view(), name="available-rooms"),
    
    # Statistics
    path("statistics/", RoomStatsView.as_view(), name="room-statistics"),
    
    # Legacy endpoints for backward compatibility
    path("addroom/", RoomCreateView.as_view(), name="room-add"),
    path("rooms/", RoomListView.as_view(), name="room-list-legacy"),
   
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)