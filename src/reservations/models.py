# Create your models here.
from django.db import models
from users.models import User
from django.core.validators import MinValueValidator

# Choices for reservation status (aligned with frontend)
RESERVATION_STATUS_CHOICES = [
    ("upcoming", "Upcoming"),
    ("past", "Past"),
    ("cancelled", "Cancelled"),
    ("booked", "Booked"),
    ("checked_in", "Checked In"),
    ("checked_out", "Checked Out"),
    ("confirmed", "Confirmed"),   # ✅ add
    ("pending", "Pending"), 
]


class Reservation(models.Model):
    """
    Model representing a hotel reservation.
    """

    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # If the user is deleted, delete all their reservations too.
    
    # Guest Information (aligned with frontend form)
    guest_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    aadhar_no = models.CharField(max_length=12, help_text="12-digit Aadhar number")
    
    # Reservation Details
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
        max_length=20, choices=RESERVATION_STATUS_CHOICES, default="upcoming"
    )
    
    # Additional fields for frontend alignment
    duration = models.CharField(max_length=50, blank=True, null=True, help_text="Stay duration description")
    room_type = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation {self.reservation_id} - Guest: {self.guest_name}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate duration based on check-in and check-out dates
        if self.check_in_date and self.check_out_date:
            delta = self.check_out_date - self.check_in_date
            days = delta.days
            if days == 0:
                self.duration = "Short (0 - 1 days)"
            elif days <= 2:
                self.duration = "Short (1 - 2 days)"
            elif days <= 4:
                self.duration = "Medium (2 - 4 days)"
            else:
                self.duration = "Long (4+ days)"
        super().save(*args, **kwargs)


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation {self.reservation.id} for Room {self.room.id}"
