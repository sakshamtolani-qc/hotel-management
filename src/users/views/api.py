from rest_framework import status, generics, permissions, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserTokenObtainPairSerializer,
)

# Custom permission: allows access only to Admin or Manager users
class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            "ADMIN",
            "MANAGER",
        ]


# Get the custom user model
User = get_user_model()


# View to handle user registration
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    # Allow any user to access this endpoint (public signup)
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # Restrict creation of ADMIN users only to authenticated admins
            if serializer.validated_data.get("user_type") == "ADMIN":
                if not request.user.is_authenticated or request.user.user_type != "ADMIN":
                    return Response(
                        {"error": "Only admin users can create other admin users"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            try:
                # Save the new user
                user = serializer.save()
                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "message": "User created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except serializers.ValidationError as e:
                # Handle validation errors
                return Response(e.detail, status=status.HTTP_403_FORBIDDEN)

        # If serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Custom JWT token view using a custom serializer
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


# View to get or update the profile of the logged-in user
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# View to list all users (Admin or Manager only)
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name", "user_type"]
    ordering_fields = ["username", "email", "user_type", "created_at"]
    ordering = ["username"]

    def get_queryset(self):
        queryset = User.objects.all()
        # Optional filtering by user_type via query params
        user_type = self.request.query_params.get("user_type", None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset
 