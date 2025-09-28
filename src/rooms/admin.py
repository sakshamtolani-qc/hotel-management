# Register your models here.
from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "title", "category", "guests", "beds", "price_per_night", "status", "rating")
    list_filter = ("category", "status", "beds", "guests", "wifi", "air_condition")
    search_fields = ("room_number", "title", "description")
    readonly_fields = ("room_id", "created_at", "updated_at")
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'title', 'description', 'category', 'status')
        }),
        ('Pricing', {
            'fields': ('price_per_night', 'price_range_min', 'price_range_max', 'price_range_display')
        }),
        ('Capacity & Facilities', {
            'fields': ('guests', 'beds', 'bathrooms', 'parking')
        }),
        ('Amenities', {
            'fields': ('television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen')
        }),
        ('Safety Features', {
            'fields': ('sanitizers', 'fire_extinguisher', 'daily_cleaning')
        }),
        ('Media & Rating', {
            'fields': ('image', 'additional_images', 'rating', 'is_favorite')
        }),
        ('System Information', {
            'fields': ('room_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
