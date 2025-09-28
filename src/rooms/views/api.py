# Example ViewSet:
# class RoomViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = RoomSerializer
#     queryset = Room.objects.all()
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Room
from ..serializers import RoomSerializer
from django.shortcuts import get_object_or_404

class RoomListView(APIView):
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomDetailView(APIView):
    def get(self, request, room_number):
        room = get_object_or_404(Room, room_number = room_number)
        serializer = RoomSerializer(room)
        return Response(serializer.data)


class RoomCreateView(APIView):
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            
            # Optional: Handle multiple images if sent
            # images = request.FILES.getlist("images")
            # for img in images:
            #     RoomImage.objects.create(room=room, image=img)

            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)