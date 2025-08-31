# Register your models here.
from django.contrib import admin
from reservations.models import RoomReservation, Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "reservation_id",
        "user",
        "check_in_date",
        "check_out_date",
        "number_of_guests",
        "total_amount",
        "reservation_status",
    )
    list_filter = ("reservation_status", "check_in_date", "check_out_date", "created_at")


@admin.register(RoomReservation)
class RoomReservationAdmin(admin.ModelAdmin):
    list_display = (
        "reservation",
        "room",
        "created_at",
    )
