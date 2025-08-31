from django.db import models
from django.core.validators import MinValueValidator

# Choices for ENUM fields
ROOM_TYPE_CHOICES = [
    ('Single', 'Single'),
    ('Double', 'Double'),
    ('Suite', 'Suite'),
]

BED_TYPE_CHOICES = [
    ('Single', 'Single'),
    ('Double', 'Double'),
    ('King', 'King'),
    ('Queen', 'Queen'),
]

ROOM_STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Occupied', 'Occupied'),
    ('Maintenance', 'Maintenance'),
]

class Room(models.Model):
    """
    Model representing a hotel room.
    """
    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10, unique=True)  
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])  # Room must hold atleast one person
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2)  
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='Available')

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type} ({self.status})"
