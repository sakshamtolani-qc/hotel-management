from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from cloudinary.models import CloudinaryField

# Choices aligned with frontend
ROOM_CATEGORY_CHOICES = [
    ("Standard", "Standard"),
    ("Deluxe", "Deluxe"),
    ("Luxury", "Luxury"),
]

ROOM_STATUS_CHOICES = [
    ("Vacant", "Vacant"),
    ("Occupied", "Occupied"),
    ("Dirty", "Dirty"),
    ("Maintenance", "Maintenance"),
]

BED_TYPE_CHOICES = [
    ("Single", "Single"),
    ("Double", "Double"),
    ("King", "King"),
    ("Queen", "Queen"),
]


class Room(models.Model):
    """
    Model representing a hotel room - aligned with frontend.
    """

    room_id = models.AutoField(primary_key=True)
    
    # Basic Room Information
    room_number = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200, help_text="Room title (e.g., 'Deluxe Double Room')")
    description = models.TextField(help_text="Room description")
    category = models.CharField(max_length=20, choices=ROOM_CATEGORY_CHOICES, default="Standard")
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_display = models.CharField(max_length=100, blank=True, help_text="E.g., ₹ 1,500 - 2,500 INR")
    
    # Room Status
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default="Vacant")
    
    # Room Amenities/Facilities
    beds = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    bathrooms = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    parking = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    guests = models.IntegerField(default=1, validators=[MinValueValidator(1)], help_text="Maximum occupancy")
    
    # Amenities (Boolean fields)
    television = models.BooleanField(default=False)
    wifi = models.BooleanField(default=True)
    washer = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    air_condition = models.BooleanField(default=True)
    kitchen = models.BooleanField(default=False)
    
    # Safety features
    sanitizers = models.BooleanField(default=True)
    fire_extinguisher = models.BooleanField(default=True)
    daily_cleaning = models.BooleanField(default=True)
    
    # Rating and favorites
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=4.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    is_favorite = models.BooleanField(default=False)
    
    # Images
    # image = models.CharField(max_length=500, blank=True, help_text="Primary room image URL")
    # additional_images = models.JSONField(
    #     default=list, blank=True, 
    #     help_text="Array of additional image URLs"
    # )
    # image = models.ImageField(upload_to='rooms/', blank=True, null=True)  # main image
    # additional_images = models.JSONField(default=list, blank=True)  # extra images
    
    
    # Main image stored in Cloudinary
    image = CloudinaryField('image', folder='hms/rooms', blank=True, null=True)

    # Additional images stored in Cloudinary
    # Store Cloudinary public_ids in JSONField
    additional_images = models.JSONField(default=list, blank=True, help_text="List of Cloudinary public_ids")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room_number']

    def __str__(self):
        return f"Room {self.room_number} - {self.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-generate price range display if not provided
        if not self.price_range_display and self.price_range_min and self.price_range_max:
            self.price_range_display = f"₹ {int(self.price_range_min):,} - {int(self.price_range_max):,} INR"
        elif not self.price_range_display:
            self.price_range_display = f"₹ {int(self.price_per_night):,} INR"
        super().save(*args, **kwargs)
    
    def get_amenities_dict(self):
        """Return amenities in frontend format"""
        return {
            'beds': self.beds,
            'guests': self.guests,
            'bathrooms': self.bathrooms,
            'rating': float(self.rating)
        }
    
    def get_amenities_list(self):
        """Return list of available amenities"""
        amenities = []
        if self.television: amenities.append('Television')
        if self.wifi: amenities.append('WiFi')
        if self.washer: amenities.append('Washer')
        if self.balcony: amenities.append('Balcony')
        if self.air_condition: amenities.append('Air Conditioning')
        if self.kitchen: amenities.append('Kitchen')
        return amenities
    
    def get_safety_features(self):
        """Return list of safety features"""
        safety = []
        if self.sanitizers: safety.append('Sanitizers')
        if self.fire_extinguisher: safety.append('Fire Extinguisher')
        if self.daily_cleaning: safety.append('Daily Cleaning')
        return safety
    
    def is_available_for_dates(self, check_in, check_out):
        """Check if room is available for given date range"""
        from reservations.models import Reservation
        
        if self.status != 'Vacant':
            return False
            
        # Check for overlapping reservations
        overlapping_reservations = Reservation.objects.filter(
            room_reservations__room=self,
            reservation_status__in=['upcoming', 'booked', 'checked_in'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        return not overlapping_reservations.exists()
