from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime
from ..models import Reservation, RoomReservation
from ..serializers import (
    ReservationSerializer, 
    ReservationCreateSerializer, 
    ReservationListSerializer, 
    ReservationUpdateSerializer,
    RoomReservationSerializer
)
from rooms.models import Room
from users.models import User

# ViewSet for complete CRUD operations
class ReservationViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD ViewSet for Reservations with filtering and search
    """
    queryset = Reservation.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['reservation_status', 'number_of_guests', 'check_in_date', 'check_out_date']
    search_fields = ['guest_name', 'email', 'phone_number', 'aadhar_no', 'room_type']
    ordering_fields = ['created_at', 'check_in_date', 'total_amount', 'guest_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        elif self.action == 'list':
            return ReservationListSerializer
        elif self.action in ['update', 'partial_update']:
            return ReservationUpdateSerializer
        return ReservationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter and status_filter != 'all':
            if status_filter == 'upcoming':
                queryset = queryset.filter(check_in_date__gte=date.today())
            elif status_filter == 'past':
                queryset = queryset.filter(check_out_date__lt=date.today())
            else:
                queryset = queryset.filter(reservation_status=status_filter)

        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(check_in_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(check_out_date__lte=date_to)

        return queryset

    def create(self, request, *args, **kwargs):
        # Handle user assignment if not provided
        if 'user' not in request.data:
            # Create or get default user (for demo purposes)
            user, created = User.objects.get_or_create(
                email=request.data.get('email'),
                defaults={
                    'username': request.data.get('email', f"user_{datetime.now().timestamp()}"),
                    'first_name': request.data.get('name', '').split(' ')[0],
                    'last_name': ' '.join(request.data.get('name', '').split(' ')[1:]) if len(request.data.get('name', '').split(' ')) > 1 else ''
                }
            )
            request.data['user'] = user.id
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        reservation.reservation_status = 'cancelled'
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response({
            'message': 'Reservation cancelled successfully',
            'reservation': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        """Check-in a reservation"""
        reservation = self.get_object()
        reservation.reservation_status = 'checked_in'
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response({
            'message': 'Check-in successful',
            'reservation': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Check-out a reservation"""
        reservation = self.get_object()
        reservation.reservation_status = 'checked_out'
        reservation.save()
        serializer = self.get_serializer(reservation)
        return Response({
            'message': 'Check-out successful',
            'reservation': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get reservation statistics"""
        queryset = self.get_queryset()
        total = queryset.count()
        upcoming = queryset.filter(reservation_status='upcoming').count()
        past = queryset.filter(reservation_status__in=['checked_out', 'past']).count()
        cancelled = queryset.filter(reservation_status='cancelled').count()
        checked_in = queryset.filter(reservation_status='checked_in').count()
        
        return Response({
            'total_reservations': total,
            'upcoming': upcoming,
            'past': past,
            'cancelled': cancelled,
            'currently_checked_in': checked_in,
        })


# Backward compatibility - List / View Reservations
class ReservationListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        status_filter = request.query_params.get('status', 'all')
        search = request.query_params.get('search', '')

        queryset = Reservation.objects.all().order_by('-created_at')
        
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        if status_filter != 'all':
            if status_filter == 'upcoming':
                queryset = queryset.filter(check_in_date__gte=date.today())
            elif status_filter == 'past':
                queryset = queryset.filter(check_out_date__lt=date.today())
            else:
                queryset = queryset.filter(reservation_status=status_filter)
        
        if search:
            queryset = queryset.filter(
                Q(guest_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(room_type__icontains=search)
            )

        serializer = ReservationListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# Create Reservation (Frontend compatible)
class ReservationCreateView(APIView):
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create or get user based on email
            user, created = User.objects.get_or_create(
                email=serializer.validated_data.get('email'),
                defaults={
                    'username': serializer.validated_data.get('email', f"user_{datetime.now().timestamp()}"),
                    'first_name': serializer.validated_data.get('guest_name', '').split(' ')[0],
                    'last_name': ' '.join(serializer.validated_data.get('guest_name', '').split(' ')[1:]) if len(serializer.validated_data.get('guest_name', '').split(' ')) > 1 else ''
                }
            )
            
            # Create reservation
            reservation = serializer.save(user=user)
            
            # Return response in frontend format
            response_serializer = ReservationSerializer(reservation)
            return Response({
                'message': 'Reservation created successfully',
                'reservation': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get single reservation detail
class ReservationDetailView(APIView):
    def get(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Update Reservation Status (Check Out / Cancel)
class ReservationUpdateStatusView(APIView):
    def patch(self, request, reservation_id):
        action = request.query_params.get('action')
        if action not in ['checkout', 'cancel', 'checkin']:
            return Response({"error": "Invalid action. Use 'checkout', 'cancel', or 'checkin'"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
        if action == 'checkout':
            reservation.reservation_status = "checked_out"
        elif action == 'cancel':
            reservation.reservation_status = "cancelled"
        elif action == 'checkin':
            reservation.reservation_status = "checked_in"

        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response({
            'message': f'Reservation {action} successful',
            'reservation': serializer.data
        })


class ReservationUpdateView(APIView):
    def put(self, request, reservation_id):
        return self.update_reservation(request, reservation_id)

    def patch(self, request, reservation_id):
        return self.update_reservation(request, reservation_id, partial=True)

    def update_reservation(self, request, reservation_id, partial=False):
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
        serializer = ReservationUpdateSerializer(reservation, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ReservationSerializer(reservation)
            return Response({
                'message': 'Reservation updated successfully',
                'reservation': response_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationDeleteView(APIView):
    def delete(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
        reservation_data = ReservationSerializer(reservation).data
        reservation.delete()
        return Response({
            'message': 'Reservation deleted successfully',
            'deleted_reservation': reservation_data
        }, status=status.HTTP_200_OK)


class ReservationCancelView(APIView):
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
        reservation.reservation_status = "cancelled"
        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response({
            'message': 'Reservation cancelled successfully',
            'reservation': serializer.data
        }, status=status.HTTP_200_OK)

class RoomAssignView(APIView):
    def post(self, request):
        reservation_id = request.data.get('reservation_id')
        room_ids = request.data.get('room_ids', [])

        if not reservation_id:
            return Response({"error": "reservation_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

        assigned_rooms = []
        for room_id in room_ids:
            room = get_object_or_404(Room, id=room_id)
            obj, created = RoomReservation.objects.get_or_create(reservation=reservation, room=room)
            if created:
                assigned_rooms.append(room.id)

        serializer = ReservationSerializer(reservation)
        return Response({
            "message": f"Rooms assigned successfully: {assigned_rooms}",
            "reservation": serializer.data
        }, status=status.HTTP_200_OK)


class ReservationSearchView(APIView):
    """Advanced search for reservations"""
    def post(self, request):
        query = request.data.get('query', '')
        filters = request.data.get('filters', {})
        
        queryset = Reservation.objects.all().order_by('-created_at')
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(guest_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(aadhar_no__icontains=query) |
                Q(room_type__icontains=query)
            )
        
        # Apply filters
        if filters.get('status'):
            queryset = queryset.filter(reservation_status=filters['status'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(check_in_date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(check_out_date__lte=filters['date_to'])
        
        if filters.get('guests_min'):
            queryset = queryset.filter(number_of_guests__gte=filters['guests_min'])
        
        if filters.get('guests_max'):
            queryset = queryset.filter(number_of_guests__lte=filters['guests_max'])
        
        if filters.get('amount_min'):
            queryset = queryset.filter(total_amount__gte=filters['amount_min'])
        
        if filters.get('amount_max'):
            queryset = queryset.filter(total_amount__lte=filters['amount_max'])
        
        serializer = ReservationListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class ReservationStatsView(APIView):
    """Get detailed reservation statistics"""
    def get(self, request):
        from django.db.models import Sum, Avg, Count
        from django.db.models.functions import TruncMonth
        
        queryset = Reservation.objects.all()
        
        # Basic stats
        total_reservations = queryset.count()
        total_revenue = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        avg_booking_value = queryset.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        avg_guests = queryset.aggregate(Avg('number_of_guests'))['number_of_guests__avg'] or 0
        
        # Status breakdown
        status_stats = {}
        for status, _ in Reservation.RESERVATION_STATUS_CHOICES:
            status_stats[status] = queryset.filter(reservation_status=status).count()
        
        # Monthly stats for current year
        from datetime import datetime
        current_year = datetime.now().year
        monthly_stats = queryset.filter(
            created_at__year=current_year
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('month')
        
        return Response({
            'total_reservations': total_reservations,
            'total_revenue': float(total_revenue),
            'average_booking_value': float(avg_booking_value),
            'average_guests_per_booking': float(avg_guests),
            'status_breakdown': status_stats,
            'monthly_stats': list(monthly_stats)
        })
