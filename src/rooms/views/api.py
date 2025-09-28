from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime
from django.db.models import Sum, Avg, Count
from ..models import Room, ROOM_CATEGORY_CHOICES, ROOM_STATUS_CHOICES
from ..serializers import (
    RoomSerializer, 
    RoomListSerializer, 
    RoomCreateSerializer, 
    RoomUpdateSerializer,
    RoomAvailabilitySerializer,
    RoomSearchSerializer
)
from reservations.models import Reservation


class RoomViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD ViewSet for Rooms with filtering, search and availability checking
    """
    queryset = Room.objects.all().order_by('room_number')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'beds', 'bathrooms', 'guests']
    search_fields = ['room_number', 'title', 'description']
    ordering_fields = ['room_number', 'price_per_night', 'created_at', 'rating']
    ordering = ['room_number']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RoomCreateSerializer
        elif self.action == 'list':
            return RoomListSerializer
        elif self.action in ['update', 'partial_update']:
            return RoomUpdateSerializer
        return RoomSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        # Filter by status 
        status_filter = self.request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Guest capacity filtering
        min_guests = self.request.query_params.get('min_guests')
        max_guests = self.request.query_params.get('max_guests')
        if min_guests:
            queryset = queryset.filter(guests__gte=min_guests)
        if max_guests:
            queryset = queryset.filter(guests__lte=max_guests)
        
        # Availability filtering
        check_in = self.request.query_params.get('check_in_date')
        check_out = self.request.query_params.get('check_out_date')
        if check_in and check_out:
            # Get room IDs that are already booked for this period
            booked_room_ids = Reservation.objects.filter(
                reservation_status__in=['upcoming', 'booked', 'checked_in'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).values_list('room_reservations__room_id', flat=True)
            
            queryset = queryset.exclude(room_id__in=booked_room_ids)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle room favorite status"""
        room = self.get_object()
        room.is_favorite = not room.is_favorite
        room.save()
        serializer = self.get_serializer(room)
        return Response({
            'message': f'Room {"added to" if room.is_favorite else "removed from"} favorites',
            'room': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update room status (Vacant/Occupied/Dirty/Maintenance)"""
        room = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = [choice[0] for choice in ROOM_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Choose from: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.status = new_status
        room.save()
        serializer = self.get_serializer(room)
        return Response({
            'message': f'Room status updated to {new_status}',
            'room': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def check_availability(self, request, pk=None):
        """Check if room is available for given dates"""
        room = self.get_object()
        serializer = RoomAvailabilitySerializer(data=request.data)
        
        if serializer.is_valid():
            check_in = serializer.validated_data['check_in_date']
            check_out = serializer.validated_data['check_out_date']
            required_guests = serializer.validated_data.get('guests')
            
            # Check guest capacity
            if required_guests and required_guests > room.guests:
                return Response({
                    'available': False,
                    'reason': f'Room can accommodate only {room.guests} guests, {required_guests} requested'
                })
            
            # Check availability
            is_available = room.is_available_for_dates(check_in, check_out)
            
            return Response({
                'available': is_available,
                'room': RoomSerializer(room).data,
                'dates': {
                    'check_in': check_in,
                    'check_out': check_out
                },
                'reason': 'Room is not available for selected dates' if not is_available else 'Room is available'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get room statistics"""
        queryset = self.get_queryset()
        
        total_rooms = queryset.count()
        vacant_rooms = queryset.filter(status='Vacant').count()
        occupied_rooms = queryset.filter(status='Occupied').count()
        dirty_rooms = queryset.filter(status='Dirty').count()
        maintenance_rooms = queryset.filter(status='Maintenance').count()
        
        avg_price = queryset.aggregate(Avg('price_per_night'))['price_per_night__avg'] or 0
        avg_rating = queryset.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Category breakdown
        category_stats = {}
        for category, _ in ROOM_CATEGORY_CHOICES:
            category_stats[category] = queryset.filter(category=category).count()
        
        return Response({
            'total_rooms': total_rooms,
            'status_breakdown': {
                'vacant': vacant_rooms,
                'occupied': occupied_rooms,
                'dirty': dirty_rooms,
                'maintenance': maintenance_rooms
            },
            'category_breakdown': category_stats,
            'average_price_per_night': round(float(avg_price), 2),
            'average_rating': round(float(avg_rating), 2),
            'occupancy_rate': round((occupied_rooms / total_rooms) * 100, 2) if total_rooms > 0 else 0
        })
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for rooms"""
        search_serializer = RoomSearchSerializer(data=request.data)
        
        if search_serializer.is_valid():
            queryset = self.get_queryset()
            filters = search_serializer.validated_data
            
            # Apply filters
            if filters.get('category') and filters['category'] != 'all':
                queryset = queryset.filter(category=filters['category'])
            
            if filters.get('status') and filters['status'] != 'all':
                queryset = queryset.filter(status=filters['status'])
            
            if filters.get('min_price'):
                queryset = queryset.filter(price_per_night__gte=filters['min_price'])
            
            if filters.get('max_price'):
                queryset = queryset.filter(price_per_night__lte=filters['max_price'])
            
            if filters.get('min_guests'):
                queryset = queryset.filter(guests__gte=filters['min_guests'])
            
            if filters.get('max_guests'):
                queryset = queryset.filter(guests__lte=filters['max_guests'])
            
            # Amenity filtering
            amenities = filters.get('amenities', [])
            for amenity in amenities:
                if amenity.lower() == 'wifi':
                    queryset = queryset.filter(wifi=True)
                elif amenity.lower() == 'television':
                    queryset = queryset.filter(television=True)
                elif amenity.lower() == 'air_conditioning':
                    queryset = queryset.filter(air_condition=True)
                elif amenity.lower() == 'kitchen':
                    queryset = queryset.filter(kitchen=True)
                elif amenity.lower() == 'balcony':
                    queryset = queryset.filter(balcony=True)
            
            # Date availability filtering
            check_in = filters.get('check_in_date')
            check_out = filters.get('check_out_date')
            if check_in and check_out:
                booked_room_ids = Reservation.objects.filter(
                    reservation_status__in=['upcoming', 'booked', 'checked_in'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                ).values_list('room_reservations__room_id', flat=True)
                
                queryset = queryset.exclude(room_id__in=booked_room_ids)
            
            serializer = RoomListSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
        
        return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Individual API Views for backward compatibility
class RoomListView(APIView):
    """List all rooms with filtering"""
    def get(self, request):
        queryset = Room.objects.all().order_by('room_number')
        
        # Apply filters
        category = request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(room_number__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        serializer = RoomListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class RoomDetailView(APIView):
    """Get single room details"""
    def get(self, request, room_id):
        room = get_object_or_404(Room, room_id=room_id)
        serializer = RoomSerializer(room)
        return Response(serializer.data)


class RoomCreateView(APIView):
    """Create new room (frontend compatible)"""
    def post(self, request):
        try:
            print(f"Received data: {request.data}")
            serializer = RoomCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                room = serializer.save()
                response_serializer = RoomSerializer(room)
                return Response({
                    'message': 'Room created successfully',
                    'room': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Error in RoomCreateView: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Handle specific database errors
            error_message = str(e)
            if "UNIQUE constraint failed: rooms_room.room_number" in error_message:
                return Response({
                    'error': 'Room number already exists',
                    'details': 'A room with this room number already exists. Please use a different room number.',
                    'field': 'roomNo'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif "UNIQUE constraint" in error_message:
                return Response({
                    'error': 'Duplicate entry',
                    'details': 'This data already exists in the system.',
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Internal server error',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomUpdateView(APIView):
    """Update room details"""
    def put(self, request, room_id):
        return self.update_room(request, room_id, partial=False)
    
    def patch(self, request, room_id):
        return self.update_room(request, room_id, partial=True)
    
    def update_room(self, request, room_id, partial=False):
        room = get_object_or_404(Room, room_id=room_id)
        serializer = RoomUpdateSerializer(room, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = RoomSerializer(room)
            return Response({
                'message': 'Room updated successfully',
                'room': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDeleteView(APIView):
    """Delete room"""
    def delete(self, request, room_id):
        room = get_object_or_404(Room, room_id=room_id)
        room_data = RoomSerializer(room).data
        room.delete()
        return Response({
            'message': 'Room deleted successfully',
            'deleted_room': room_data
        })


class RoomAvailabilityView(APIView):
    """Check room availability for specific dates"""
    def post(self, request):
        serializer = RoomAvailabilitySerializer(data=request.data)
        
        if serializer.is_valid():
            room_id = serializer.validated_data['room_id']
            check_in = serializer.validated_data['check_in_date']
            check_out = serializer.validated_data['check_out_date']
            required_guests = serializer.validated_data.get('guests')
            
            room = get_object_or_404(Room, room_id=room_id)
            
            # Check guest capacity
            if required_guests and required_guests > room.guests:
                return Response({
                    'available': False,
                    'room': RoomSerializer(room).data,
                    'reason': f'Room can accommodate only {room.guests} guests, {required_guests} requested'
                })
            
            # Check availability
            is_available = room.is_available_for_dates(check_in, check_out)
            
            return Response({
                'available': is_available,
                'room': RoomSerializer(room).data,
                'dates': {
                    'check_in': check_in,
                    'check_out': check_out
                },
                'reason': 'Room is not available for selected dates' if not is_available else 'Room is available'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableRoomsView(APIView):
    """Get all available rooms for specific dates"""
    def get(self, request):
        check_in = request.query_params.get('check_in_date')
        check_out = request.query_params.get('check_out_date')
        guests = request.query_params.get('guests')
        category = request.query_params.get('category')
        
        if not check_in or not check_out:
            return Response({
                'error': 'check_in_date and check_out_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate dates
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            if check_out_date <= check_in_date:
                return Response({
                    'error': 'Check-out date must be after check-in date'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if check_in_date < date.today():
                return Response({
                    'error': 'Check-in date cannot be in the past'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get available rooms
        queryset = Room.objects.filter(status='Vacant')
        
        # Filter by guest capacity
        if guests:
            try:
                guest_count = int(guests)
                queryset = queryset.filter(guests__gte=guest_count)
            except ValueError:
                pass
        
        # Filter by category
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        
        # Exclude rooms that are already booked for this period
        booked_room_ids = Reservation.objects.filter(
            reservation_status__in=['upcoming', 'booked', 'checked_in'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        ).values_list('room_reservations__room_id', flat=True)
        
        queryset = queryset.exclude(room_id__in=booked_room_ids)
        
        serializer = RoomListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'dates': {
                'check_in': check_in,
                'check_out': check_out
            },
            'filters': {
                'guests': guests,
                'category': category
            },
            'available_rooms': serializer.data
        })


class RoomStatsView(APIView):
    """Get detailed room statistics"""
    def get(self, request):
        from django.db.models import Sum, Avg, Count
        from django.db.models.functions import TruncMonth
        
        queryset = Room.objects.all()
        
        # Basic stats
        total_rooms = queryset.count()
        avg_price = queryset.aggregate(Avg('price_per_night'))['price_per_night__avg'] or 0
        avg_rating = queryset.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Status breakdown
        status_stats = {}
        for status, _ in ROOM_STATUS_CHOICES:
            status_stats[status] = queryset.filter(status=status).count()
        
        # Category breakdown with pricing
        category_stats = {}
        for category, _ in ROOM_CATEGORY_CHOICES:
            category_rooms = queryset.filter(category=category)
            category_stats[category] = {
                'count': category_rooms.count(),
                'avg_price': category_rooms.aggregate(Avg('price_per_night'))['price_per_night__avg'] or 0
            }
        
        # Recent room additions
        from datetime import datetime, timedelta
        current_month = datetime.now().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        recent_additions = queryset.filter(
            created_at__gte=last_month
        ).count()
        
        return Response({
            'total_rooms': total_rooms,
            'average_price_per_night': round(float(avg_price), 2),
            'average_rating': round(float(avg_rating), 2),
            'status_breakdown': status_stats,
            'category_breakdown': category_stats,
            'recent_additions_this_month': recent_additions,
            'occupancy_rate': round((status_stats.get('Occupied', 0) / total_rooms) * 100, 2) if total_rooms > 0 else 0
        })
