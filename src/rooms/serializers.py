from rest_framework import serializers
from .models import Room, ROOM_CATEGORY_CHOICES, ROOM_STATUS_CHOICES
from django.conf import settings
from datetime import date
import re
import os
import uuid
from django.core.files.storage import default_storage


class RoomSerializer(serializers.ModelSerializer):
    price_per_night = serializers.SerializerMethodField()
    price_range_min = serializers.SerializerMethodField()
    price_range_max = serializers.SerializerMethodField()
    
    id = serializers.SerializerMethodField()
    priceRange = serializers.CharField(source='price_range_display', read_only=True)
    amenities = serializers.SerializerMethodField()
    isFavorite = serializers.BooleanField(source='is_favorite')
    images = serializers.SerializerMethodField()
    
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    amenities_list = serializers.SerializerMethodField()
    safety_features = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_id', 'room_number', 'title', 'description', 'category', 'status',
            'price_per_night', 'price_range_min', 'price_range_max', 'priceRange',
            'beds', 'bathrooms', 'parking', 'guests',
            'television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen',
            'sanitizers', 'fire_extinguisher', 'daily_cleaning',
            'rating', 'isFavorite', 'image', 'additional_images', 'images',
            'amenities', 'amenities_list', 'safety_features',
            'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["additional_images"] = ret.get("additional_images") or []
        return ret
    
    def get_id(self, obj):
        return obj.room_id
    
    def get_amenities(self, obj):
        return obj.get_amenities_dict()
    
    def get_amenities_list(self, obj):
        return obj.get_amenities_list()
    
    def get_safety_features(self, obj):
        return obj.get_safety_features()
    def get_images(self, obj):
        images = []
        if obj.image:
            images.append(obj.image.url if hasattr(obj.image, 'url') else str(obj.image))
        if obj.additional_images:
            # Assuming additional_images is a list of file paths
            images.extend([settings.MEDIA_URL + str(img) for img in obj.additional_images])
        return images

    # def get_images(self, obj):
    #     images = []
    #     if obj.image:
    #         images.append(obj.image)
    #     if obj.additional_images:
    #         images.extend(obj.additional_images)
    #     return images
    
    def get_price_per_night(self, obj):
        return float(obj.price_per_night) if obj.price_per_night is not None else None

    def get_price_range_min(self, obj):
        return float(obj.price_range_min) if obj.price_range_min is not None else None

    def get_price_range_max(self, obj):
        return float(obj.price_range_max) if obj.price_range_max is not None else None


class RoomListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    priceRange = serializers.CharField(source='price_range_display', read_only=True)
    amenities = serializers.SerializerMethodField()
    isFavorite = serializers.BooleanField(source='is_favorite')
    
    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'priceRange', 'image', 
            'status', 'category', 'amenities', 'isFavorite'
        ]
    
    def get_id(self, obj):
        return obj.room_id
    
    def get_amenities(self, obj):
        return {
            'beds': obj.beds,
            'guests': obj.guests,
            'bathrooms': obj.bathrooms,
            'rating': float(obj.rating)
        }


class RoomCreateSerializer(serializers.ModelSerializer):
    roomNo = serializers.CharField(source='room_number', max_length=10)
    priceRange = serializers.CharField(source='price_range_display', required=False)
    roomDescription = serializers.CharField(source='description')
    
    image = serializers.ImageField(required=True)
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True
    )
    
    facilities = serializers.SerializerMethodField(read_only=True)
    amenities = serializers.SerializerMethodField(read_only=True)
    safety = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'roomNo', 'title', 'roomDescription', 'category', 'price_per_night',
            'price_range_min', 'price_range_max', 'priceRange',
            'beds', 'bathrooms', 'parking', 'guests',
            'television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen',
            'sanitizers', 'fire_extinguisher', 'daily_cleaning',
            'rating', 'image', 'additional_images',
            'facilities', 'amenities', 'safety'
        ]
    
    def create(self, validated_data):
        additional_images = validated_data.pop('additional_images', [])
        room = Room.objects.create(**validated_data)

        saved_files = []
        # Save additional images with unique names
        for img in additional_images:
            ext = img.name.split('.')[-1]
            unique_name = f"rooms/{uuid.uuid4().hex}.{ext}"
            path = default_storage.save(unique_name, img)
            saved_files.append(path)

        room.additional_images = saved_files
        room.save()
        return room

    
    def get_facilities(self, obj):
        return {'beds': obj.beds, 'bathrooms': obj.bathrooms, 'parking': obj.parking}
    
    def get_amenities(self, obj):
        return {
            'television': obj.television,
            'wifi': obj.wifi,
            'washer': obj.washer,
            'balcony': obj.balcony,
            'airCondition': obj.air_condition,
            'kitchen': obj.kitchen,
            'other': False
        }
    
    def get_safety(self, obj):
        return {
            'sanitizers': obj.sanitizers,
            'fireThrowers': obj.fire_extinguisher,
            'dailyCleaner': obj.daily_cleaning,
            'option1': False,
            'option2': False,
            'option3': False,
            'option4': False,
            'option5': False
        }
    
    def validate_roomNo(self, value):
        if not re.match(r'^[A-Za-z0-9]{1,10}$', value):
            raise serializers.ValidationError("Room number can only contain letters and numbers")
        return value
    
    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
    
    def validate_beds(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must have at least 1 bed")
        return value
    
    def validate_guests(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must accommodate at least 1 guest")
        return value


class RoomUpdateSerializer(serializers.ModelSerializer):
    roomNo = serializers.CharField(source='room_number', required=False)
    priceRange = serializers.CharField(source='price_range_display', required=False)
    roomDescription = serializers.CharField(source='description', required=False)
    isFavorite = serializers.BooleanField(source='is_favorite', required=False)
    
    class Meta:
        model = Room
        fields = [
            'roomNo', 'title', 'roomDescription', 'category', 'status',
            'price_per_night', 'price_range_min', 'price_range_max', 'priceRange',
            'beds', 'bathrooms', 'parking', 'guests',
            'television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen',
            'sanitizers', 'fire_extinguisher', 'daily_cleaning',
            'rating', 'isFavorite', 'image', 'additional_images'
        ]
        extra_kwargs = {field: {'required': False} for field in fields}
    
    def validate_roomNo(self, value):
        if value and not re.match(r'^[A-Za-z0-9]{1,10}$', value):
            raise serializers.ValidationError("Room number can only contain letters and numbers")
        return value
    
    def validate_price_per_night(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value


class RoomAvailabilitySerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    guests = serializers.IntegerField(min_value=1, required=False)
    
    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out date must be after check-in date")
            if check_in < date.today():
                raise serializers.ValidationError("Check-in date cannot be in the past")
        return data


class RoomSearchSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=[('all', 'All')] + ROOM_CATEGORY_CHOICES, default='all')
    status = serializers.ChoiceField(choices=[('all', 'All')] + ROOM_STATUS_CHOICES, default='all')
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_guests = serializers.IntegerField(min_value=1, required=False)
    max_guests = serializers.IntegerField(min_value=1, required=False)
    amenities = serializers.ListField(child=serializers.CharField(), required=False)
    check_in_date = serializers.DateField(required=False)
    check_out_date = serializers.DateField(required=False)
    
    def validate(self, data):
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        min_guests = data.get('min_guests')
        max_guests = data.get('max_guests')
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError("Minimum price cannot be greater than maximum price")
        
        if min_guests and max_guests and min_guests > max_guests:
            raise serializers.ValidationError("Minimum guests cannot be greater than maximum guests")
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out date must be after check-in date")
            if check_in < date.today():
                raise serializers.ValidationError("Check-in date cannot be in the past")
        
        return data
