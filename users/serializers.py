from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'address', 'city', 'state', 'zip_code',
            'country', 'id_document_number', 'date_of_birth', 'user_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    is_superuser = serializers.BooleanField(write_only=True, required=False, default=False)
    is_staff = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name', 'last_name',
            'phone_number', 'address', 'city', 'state', 'zip_code', 'country',
            'id_document_number', 'date_of_birth', 'user_type', 'is_superuser', 'is_staff'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        is_superuser = validated_data.get('is_superuser', False)
        is_staff = validated_data.get('is_staff', False)

        # Only allow superuser creation if the request user is an admin and superuser
        if is_superuser or is_staff:
            if not (request and request.user.is_authenticated and 
                   request.user.is_superuser and request.user.user_type == 'ADMIN'):
                raise serializers.ValidationError({
                    "error": "Only superuser admins can create superuser or staff accounts"
                })

        validated_data.pop('password2')
        if is_superuser:
            user = User.objects.create_superuser(**validated_data)
        else:
            user = User.objects.create_user(**validated_data)
        return user

class UserTokenObtainPairSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        if '@' in username_or_email:
            user = User.objects.filter(email=username_or_email).first()
        else:
            user = User.objects.filter(username=username_or_email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
            return data
        raise serializers.ValidationError('No active account found with the given credentials')
