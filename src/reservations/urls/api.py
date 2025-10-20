# app_name = "reservations"

# urlpatterns = [
    # Add your URL patterns here
    # Example:
    # path('bookings/', views.BookingListView.as_view(), name='booking-list'),
# ]

# 👇 This line is required when you use namespace in include()
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from reservations import views

app_name = "reservations"

from reservations.views.api import (
    ReservationViewSet,
    ReservationListView, 
    ReservationCreateView, 
    ReservationDetailView,
    ReservationUpdateView,
    ReservationDeleteView,
    ReservationUpdateStatusView,
    ReservationCancelView,
    ReservationSearchView,
    ReservationStatsView,
    RoomAssignView
)

# Router for ViewSet (provides full REST API)
router = DefaultRouter()
router.register(r'api', ReservationViewSet, basename='reservation-api')

urlpatterns = [
    # ViewSet routes (Modern REST API)
    path('', include(router.urls)),
    path("reservations/", ReservationCreateView.as_view(), name="reservation-list-create"),
    
    # Individual API endpoints (Backward compatibility and specific use cases)
    path("list/", ReservationListView.as_view(), name="reservation-list"),
    path("create/", ReservationCreateView.as_view(), name="reservation-create"),
    path("<int:reservation_id>/detail/", ReservationDetailView.as_view(), name="reservation-detail"),
    path("<int:reservation_id>/update/", ReservationUpdateView.as_view(), name="reservation-update"),
    path("<int:reservation_id>/delete/", ReservationDeleteView.as_view(), name="reservation-delete"),
    path("<int:reservation_id>/update-status/", ReservationUpdateStatusView.as_view(), name="reservation-update-status"),
    path("<int:reservation_id>/cancel/", ReservationCancelView.as_view(), name="reservation-cancel"),
    
    # Advanced features
    path("search/", ReservationSearchView.as_view(), name="reservation-search"),
    path("statistics/", ReservationStatsView.as_view(), name="reservation-statistics"),
    path("room/assign/", RoomAssignView.as_view(), name="reservation-room-assign"),
]

