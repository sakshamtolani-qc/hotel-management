

# urlpatterns = [
#     # Add your URL patterns here
#     # Example:
#     # path('list/', views.RoomListView.as_view(), name='room-list'),
# ]
from django.urls import path
from ..views.api import RoomCreateView, RoomListView, RoomDetailView

app_name = "rooms"

urlpatterns = [
    path("addroom/", RoomCreateView.as_view(), name="room-add"),   # POST → /addroom
    path("rooms/", RoomListView.as_view(), name="room-list"),      # GET → /rooms
    path("rooms/<str:room_number>/", RoomDetailView.as_view(), name="room-detail"),  # GET → /rooms/<room_no>
]
