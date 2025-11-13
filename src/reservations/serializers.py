from rest_framework import serializers
from .models import Reservation, RoomReservation
from rooms.models import Room
from users.models import User
import re
from datetime import date


class RoomReservationSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='room.id', read_only=True)

    class Meta:
        model = RoomReservation
        fields = ['id', 'room_id', 'created_at', 'updated_at']


class ReservationSerializer(serializers.ModelSerializer):
    """Complete serializer for Reservation model with frontend alignment"""
    
    # Read-only fields
    reservation_id = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    
    # Frontend compatibility fields
    id = serializers.SerializerMethodField()
    guests = serializers.IntegerField(source='number_of_guests')
    price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2)
    status = serializers.CharField(source='reservation_status')
    checkIn = serializers.DateField(source='check_in_date', format='%d %b %Y')
    checkOut = serializers.DateField(source='check_out_date', format='%d %b %Y')
    guestName = serializers.CharField(source='guest_name')
    phoneNumber = serializers.CharField(source='phone_number')
    aadharNo = serializers.CharField(source='aadhar_no')
    roomType = serializers.CharField(source='room_type', allow_blank=True, default="Standard Room",required=False)
    # room_type = serializers.CharField(required=False, allow_blank=True, default="Standard Room")

    # Relations
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    room_reservations = RoomReservationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_id', 'user', 'user_id', 'guestName', 'phoneNumber', 'email', 'aadharNo',
            'checkIn', 'checkOut', 'guests', 'price', 'status', 'duration', 'roomType',
            'created_at', 'updated_at', 'room_reservations'
        ]
        extra_kwargs = {
            'user': {'write_only': True}
        }
    
    def get_id(self, obj):
        return str(obj.reservation_id)
    
    def validate_aadhar_no(self, value):
        """Validate Aadhar number format"""
        if not re.match(r'^\d{12}$', value):
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not re.match(r'^[+]?[0-9]{10,15}$', value):
            raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value
    
    def validate(self, data):
        """Custom validation for dates"""
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out and check_out < check_in:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        if check_in and check_in < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past")
        
        return data


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reservations (aligned with frontend form)"""
    
    name = serializers.CharField(source='guest_name', max_length=100)
    phoneNumber = serializers.CharField(source='phone_number', max_length=15)
    aadharNo = serializers.CharField(source='aadhar_no', max_length=12)
    checkIn = serializers.DateField(source='check_in_date')
    checkOut = serializers.DateField(source='check_out_date', required=False, allow_null=True)
    guests = serializers.IntegerField(source='number_of_guests', min_value=1)
    price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, required=False, default=1000)
    room_type = serializers.CharField(required=False, allow_blank=True, default="Standard Room")
    room_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Reservation
        fields = ['name', 'phoneNumber', 'email', 'aadharNo', 'checkIn', 'checkOut', 'guests', 'room_type', 'price', 'room_ids']
    
    def validate_aadharNo(self, value):
        if not re.match(r'^\d{12}$', value):
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits")
        return value
    
    def validate_phoneNumber(self, value):
        if not re.match(r'^[+]?[0-9]{10,15}$', value):
            raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value
    
    def validate_checkIn(self, value):
        if value < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        room_id = None

        # ✅ Try to get room ID from body
        if request and hasattr(request, "data"):
            room_id = (
                request.data.get('room_id')
                or request.data.get('room')
                or request.data.get('roomId')
            )

        # ✅ Or from query string (?roomId=11)
        if request and hasattr(request, "query_params") and not room_id:
            room_id = request.query_params.get('roomId')

        # ✅ Or handle list of rooms from frontend
        room_ids = request.data.get('room_ids', [])
        if not room_ids and room_id:
            room_ids = [room_id]

        validated_data['reservation_status'] = 'upcoming'

        # ✅ Create reservation record
        reservation = super().create(validated_data)

        # ✅ Create RoomReservation(s)
        from rooms.models import Room
        from .models import RoomReservation
        for rid in room_ids:
            room = Room.objects.filter(id=rid).first()
            if room:
                RoomReservation.objects.create(reservation=reservation, room=room)
                print(f">>> RoomReservation created for Room ID {rid}")
            else:
                print(f">>> Room ID {rid} not found, skipping.")

        return reservation


    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        if check_out and check_out < check_in:
            raise serializers.ValidationError("Check-out date cannot be before check-in")
        return data


class ReservationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing reservations"""
    
    id = serializers.SerializerMethodField()
    guestName = serializers.CharField(source='guest_name')
    checkIn = serializers.DateField(source='check_in_date', format='%d %b %Y')
    checkOut = serializers.DateField(source='check_out_date', format='%d %b %Y')
    guests = serializers.IntegerField(source='number_of_guests')
    price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2)
    status = serializers.CharField(source='reservation_status')
    room_type = serializers.CharField(source="roomType", read_only=True)  # 👈 matches field name

    class Meta:
        model = Reservation
        fields = ['id', 'guestName', 'room_type', 'checkIn', 'checkOut', 'duration', 'guests', 'price', 'status', 'created_at']

    def get_id(self, obj):
        return str(obj.reservation_id)


class ReservationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reservations"""
    
    guestName = serializers.CharField(source='guest_name', required=False)
    phoneNumber = serializers.CharField(source='phone_number', required=False)
    aadharNo = serializers.CharField(source='aadhar_no', required=False)
    checkIn = serializers.DateField(source='check_in_date', required=False)
    checkOut = serializers.DateField(source='check_out_date', required=False)
    guests = serializers.IntegerField(source='number_of_guests', required=False)
    price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, required=False)
    status = serializers.CharField(source='reservation_status', required=False)
    
    class Meta:
        model = Reservation
        fields = ['guestName', 'phoneNumber', 'email', 'aadharNo', 'checkIn', 'checkOut', 'guests', 'room_type', 'price', 'status']
    
    def validate_aadharNo(self, value):
        if value and not re.match(r'^\d{12}$', value):
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits")
        return value
    
    def validate_phoneNumber(self, value):
        if value and not re.match(r'^[+]?[0-9]{10,15}$', value):
            raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value
