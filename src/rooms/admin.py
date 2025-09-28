# Register your models here.
from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "capacity", "bed_type", "price_per_night", "status")
    list_filter = ("room_type", "status", "bed_type")
    search_fields = ("room_number",)
