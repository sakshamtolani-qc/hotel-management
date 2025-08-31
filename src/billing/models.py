# Create your models here.

from django.db import models
from users.models import User
from django.core.validators import MinValueValidator

# Choices for reservation status
RESERVATION_STATUS_CHOICES = [
    ("Booked", "Booked"),
    ("Checked In", "Checked In"),
    ("Checked Out", "Checked Out"),
    ("Cancelled", "Cancelled"),
]


class Reservation(models.Model):
    """
    Model representing a hotel reservation.
    """

    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # If the user is deleted, delete all their reservations too.
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField(
        validators=[MinValueValidator(1)]  # At least 1 guest required
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.0)],  # prevents 0 or negative amounts
    )
    reservation_status = models.CharField(
        max_length=20, choices=RESERVATION_STATUS_CHOICES, default="Booked"
    )

    def __str__(self):
        return f"Reservation {self.reservation_id} - User: {self.user}"


class RoomReservation(models.Model):
    # Foreign Key to the Reservation model
    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.CASCADE,
        related_name="room_reservations",
    )

    # Foreign Key to the Room model
    room = models.ForeignKey(
        "rooms.Room", on_delete=models.CASCADE, related_name="room_reservations"
    )

    def __str__(self):
        return f"Reservation {self.reservation.id} for Room {self.room.id}"
