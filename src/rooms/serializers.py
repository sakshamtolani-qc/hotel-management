import re
from datetime import date
from rest_framework import serializers
from .models import Room, ROOM_CATEGORY_CHOICES, ROOM_STATUS_CHOICES
import cloudinary.uploader
import cloudinary

# -----------------------------
# Helper Functions
# -----------------------------
def build_cloudinary_url(image):
    """
    Helper to convert a CloudinaryResource or public_id to full URL.
    Returns None if image is None.
    """
    if image:
        return cloudinary.CloudinaryImage(str(image)).build_url()
    return None


# -----------------------------
# Main Room Serializer (Detailed)
# -----------------------------
class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed room info.
    Includes main image, additional images, amenities, safety features, and frontend-ready fields.
    """
    id = serializers.SerializerMethodField()
    price_per_night = serializers.SerializerMethodField()
    price_range_min = serializers.SerializerMethodField()
    price_range_max = serializers.SerializerMethodField()
    priceRange = serializers.CharField(source='price_range_display', read_only=True)
    amenities = serializers.SerializerMethodField()
    amenities_list = serializers.SerializerMethodField()
    safety_features = serializers.SerializerMethodField()
    isFavorite = serializers.BooleanField(source='is_favorite')
    image = serializers.SerializerMethodField()  # Main image
    images = serializers.SerializerMethodField()  # All images including additional
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Room
        fields = [
            'id', 'room_id', 'room_number', 'title', 'description', 'category', 'status',
            'price_per_night', 'price_range_min', 'price_range_max', 'priceRange',
            'beds', 'bathrooms', 'parking', 'guests',
            'television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen',
            'sanitizers', 'fire_extinguisher', 'daily_cleaning',
            'rating', 'isFavorite','image', 'images',
            'amenities', 'amenities_list', 'safety_features',
            'created_at', 'updated_at'
        ]

    # -----------------------------
    # SerializerMethodField Methods
    # -----------------------------
    def get_id(self, obj):
        return obj.room_id

    def get_price_per_night(self, obj):
        return float(obj.price_per_night) if obj.price_per_night is not None else None

    def get_price_range_min(self, obj):
        return float(obj.price_range_min) if obj.price_range_min is not None else None

    def get_price_range_max(self, obj):
        return float(obj.price_range_max) if obj.price_range_max is not None else None

    # def get_amenities(self, obj):
    #     """
    #     Returns amenities as a dict for frontend.
    #     """
    #     return obj.get_amenities_dict()
    def get_amenities(self, obj):
        return {
            'beds': obj.beds,
            'guests': obj.guests,
            'bathrooms': obj.bathrooms,
            'rating': float(obj.rating) if obj.rating else None,
            'television': obj.television,
            'wifi': obj.wifi,
            'washer': obj.washer,
            'balcony': obj.balcony,
            'airCondition': obj.air_condition,
            'kitchen': obj.kitchen,
            'sanitizers': obj.sanitizers,
            'fireExtinguishers': obj.fire_extinguisher,
            'dailyCleaner': obj.daily_cleaning,
        }


    def get_amenities_list(self, obj):
        return obj.get_amenities_list()

    def get_safety_features(self, obj):
        return obj.get_safety_features()

    def get_image(self, obj):
        """
        Returns only the main image URL for frontend.
        """
        return build_cloudinary_url(obj.image)

    def get_images(self, obj):
        """
        Returns all images (main + additional) as full Cloudinary URLs.
        """
        image_list = []
        if obj.image:
            image_list.append(build_cloudinary_url(obj.image))
        if obj.additional_images:
            image_list.extend([build_cloudinary_url(img) for img in obj.additional_images])
        return image_list

    # def get_image(self, obj):
    #     return build_cloudinary_url(obj.image)
# -----------------------------
# Room List Serializer (Minimal for Grids)
# -----------------------------
class RoomListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    priceRange = serializers.CharField(source='price_range_display', read_only=True)
    amenities = serializers.SerializerMethodField()
    isFavorite = serializers.BooleanField(source='is_favorite')
    image = serializers.SerializerMethodField()  # Only main image

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
            'rating': float(obj.rating) if obj.rating else None
        }

    def get_image(self, obj):
        return build_cloudinary_url(obj.image)


# -----------------------------
# Room Create Serializer
# -----------------------------
class RoomCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Room instances.
    Uploads images to Cloudinary automatically.
    """
    roomNo = serializers.CharField(source='room_number', max_length=10)
    roomDescription = serializers.CharField(source='description')
    priceRange = serializers.CharField(source='price_range_display', required=False)
    image = serializers.ImageField(required=True)
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True
    )

    # Frontend computed fields
    facilities = serializers.SerializerMethodField(read_only=True)
    amenities_info = serializers.SerializerMethodField(read_only=True)
    safety_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'roomNo', 'title', 'roomDescription', 'category', 'price_per_night',
            'price_range_min', 'price_range_max', 'priceRange',
            'beds', 'bathrooms', 'parking', 'guests',
            'television', 'wifi', 'washer', 'balcony', 'air_condition', 'kitchen',
            'sanitizers', 'fire_extinguisher', 'daily_cleaning',
            'rating', 'image', 'additional_images',
            'facilities', 'amenities_info', 'safety_info'
        ]

    # -----------------------------
    # Cloudinary Image Upload
    # -----------------------------
    def create(self, validated_data):
        additional_images = validated_data.pop('additional_images', [])
        main_image = validated_data.pop('image', None)

        # Upload main image
        if main_image:
            result = cloudinary.uploader.upload(main_image, folder="hms/rooms")
            validated_data['image'] = result['public_id']

        # Create room instance
        room = Room.objects.create(**validated_data)

        # Upload additional images
        saved_images = []
        for img in additional_images:
            result = cloudinary.uploader.upload(img, folder="hms/rooms")
            saved_images.append(result['public_id'])
        room.additional_images = saved_images
        room.save()
        return room

    # -----------------------------
    # Frontend Fields
    # -----------------------------
    def get_facilities(self, obj):
        return {'beds': obj.beds, 'bathrooms': obj.bathrooms, 'parking': obj.parking}

    def get_amenities_info(self, obj):
        return {
            'television': obj.television,
            'wifi': obj.wifi,
            'washer': obj.washer,
            'balcony': obj.balcony,
            'airCondition': obj.air_condition,
            'kitchen': obj.kitchen,
        }

    def get_safety_info(self, obj):
        return {
            'sanitizers': obj.sanitizers,
            'fireExtinguishers': obj.fire_extinguisher,
            'dailyCleaner': obj.daily_cleaning,
        }

    # -----------------------------
    # Field Validations
    # -----------------------------
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


# -----------------------------
# Room Update Serializer
# -----------------------------
class RoomUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Room instances.
    Handles Cloudinary image replacement safely.
    """
    roomNo = serializers.CharField(source='room_number', required=False)
    roomDescription = serializers.CharField(source='description', required=False)
    priceRange = serializers.CharField(source='price_range_display', required=False)
    isFavorite = serializers.BooleanField(source='is_favorite', required=False)
    image = serializers.ImageField(required=False)
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True
    )

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

    # -----------------------------
    # Validation
    # -----------------------------
    def validate_roomNo(self, value):
        if value and not re.match(r'^[A-Za-z0-9]{1,10}$', value):
            raise serializers.ValidationError("Room number can only contain letters and numbers")
        return value

    def validate_price_per_night(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    # -----------------------------
    # Update Method
    # -----------------------------
    def update(self, instance, validated_data):
        # Update main image
        new_image = validated_data.pop('image', None)
        if new_image:
            if instance.image:
                try:
                    cloudinary.uploader.destroy(instance.image)
                except Exception:
                    pass
            result = cloudinary.uploader.upload(new_image, folder="hms/rooms")
            instance.image = result['public_id']

        # Update additional images
        new_additional_images = validated_data.pop('additional_images', None)
        if new_additional_images is not None:
            if instance.additional_images:
                for pub_id in instance.additional_images:
                    try:
                        cloudinary.uploader.destroy(pub_id)
                    except Exception:
                        pass
            uploaded_ids = [cloudinary.uploader.upload(img, folder="hms/rooms")['public_id'] for img in new_additional_images]
            instance.additional_images = uploaded_ids

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# -----------------------------
# Room Availability Serializer
# -----------------------------
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


# -----------------------------
# Room Search Serializer
# -----------------------------
class RoomSearchSerializer(serializers.Serializer):
    """
    Serializer for filtering/searching rooms.
    Returns frontend-ready fields like image, amenities, rating, and isFavorite.
    """
    category = serializers.ChoiceField(choices=[('all', 'All')] + ROOM_CATEGORY_CHOICES, default='all')
    status = serializers.ChoiceField(choices=[('all', 'All')] + ROOM_STATUS_CHOICES, default='all')
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_guests = serializers.IntegerField(min_value=1, required=False)
    max_guests = serializers.IntegerField(min_value=1, required=False)
    amenities = serializers.ListField(child=serializers.CharField(), required=False)
    check_in_date = serializers.DateField(required=False)
    check_out_date = serializers.DateField(required=False)

    # Frontend fields
    id = serializers.SerializerMethodField()
    title = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField()
    amenities_info = serializers.SerializerMethodField()
    isFavorite = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def validate(self, data):
        # Price validation
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError("Minimum price cannot be greater than maximum price")

        # Guest validation
        min_guests = data.get('min_guests')
        max_guests = data.get('max_guests')
        if min_guests and max_guests and min_guests > max_guests:
            raise serializers.ValidationError("Minimum guests cannot be greater than maximum guests")

        # Date validation
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out date must be after check-in date")
            if check_in < date.today():
                raise serializers.ValidationError("Check-in date cannot be in the past")
        return data

    # -----------------------------
    # SerializerMethodField Methods
    # -----------------------------
    def get_id(self, obj):
        return obj.room_id

    def get_image(self, obj):
        return build_cloudinary_url(obj.image)

    def get_amenities_info(self, obj):
        return {
            'beds': obj.beds,
            'guests': obj.guests,
            'bathrooms': obj.bathrooms,
            'rating': float(obj.rating) if obj.rating else None,
            'television': obj.television,
            'wifi': obj.wifi,
            'washer': obj.washer,
            'balcony': obj.balcony,
            'airCondition': obj.air_condition,
            'kitchen': obj.kitchen,
        }

    def get_isFavorite(self, obj):
        return obj.is_favorite

    def get_rating(self, obj):
        return float(obj.rating) if obj.rating else None
