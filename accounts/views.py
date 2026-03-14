from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

from .serializers import SendOTPSerializer, VerifyOTPSerializer, MyTokenObtainPairSerializer, UserSerializer
from .models import OTPRequest
from .utils import generate_verification_code, send_verification_email
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class SendOTPView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Check if already a user
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Rate limit or check if existing OTP request
        otp_request, created = OTPRequest.objects.get_or_create(email=email)
        
        if not created and timezone.now() < otp_request.created_at + timedelta(minutes=1):
            return Response({'error': 'Please wait before requesting another OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            
        otp_request.username = username
        otp_request.password_hash = make_password(password)
        code = generate_verification_code()
        otp_request.otp_code = code
        otp_request.created_at = timezone.now()
        otp_request.attempts = 0
        otp_request.save()
        
        # Mocking user object for send_verification_email
        class MockUser:
            pass
        mock_user = MockUser()
        mock_user.email = email
        
        email_sent = send_verification_email(mock_user, code)
        
        if not email_sent:
            return Response({'error': 'Failed to send OTP email. Please try again later.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
#n
class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        try:
            otp_request = OTPRequest.objects.get(email=email)
        except OTPRequest.DoesNotExist:
            return Response({'error': 'No pending registration.'}, status=status.HTTP_404_NOT_FOUND)
            
        if timezone.now() > otp_request.created_at + timedelta(minutes=5):
            return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if otp_request.otp_code != code:
            otp_request.attempts += 1
            otp_request.save()
            if otp_request.attempts >= 3:
                otp_request.delete()
                return Response({'error': 'Too many failed attempts. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create the actual user
        user = User.objects.create(
            username=otp_request.username,
            email=otp_request.email,
            password=otp_request.password_hash,
            is_verified=True
        )
        
        otp_request.delete()
        
        return Response({'message': 'Registration successful. You can now login.'}, status=status.HTTP_201_CREATED)
class SearchUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return get_user_model().objects.filter(username__icontains=query).exclude(id=self.request.user.id)
        return get_user_model().objects.none()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
