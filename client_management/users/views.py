from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, PasswordResetSerializer, SetNewPasswordSerializer
from django.contrib.auth import authenticate, get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny,IsAuthenticated

User = get_user_model()

class RegisterView(APIView):
    """
    Only Admins and Managers can create new users.
    Employee-specific fields are required if role='employee'.
    """
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        if request.user.role not in ['admin', 'manager']:
            return Response({"error": "You do not have permission to create users."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": getattr(user, "role", "")
                }
            })
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If the email exists, a reset link will be sent"}, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # reset_link = f"http://127.0.0.1:8000/api/users/password-reset-confirm/?uid={uid}&token={token}"

        reset_link = f"http://127.0.0.1:3000/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="Password Reset",
            message=f"Click here to reset your password: {reset_link}",
            from_email=None, 
            recipient_list=[email],
        )

        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = urlsafe_base64_decode(serializer.validated_data['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid UID"}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
