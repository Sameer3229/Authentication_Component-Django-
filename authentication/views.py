from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer, PasswordResetRequestSerializer, SetNewPasswordSerializer
from . models import OneTimePassword
from django.contrib.auth import get_user_model
from .utils import send_otp_via_email, send_password_reset_otp, send_password_success_email
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate


User = get_user_model()

class SignupView(GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User created successfully. Check your email for the 6-digit code."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(GenericAPIView):
    def post(self, request):
        email = request.data.get('email')
        code =  request.data.get('code')

        if not email or not code:
            return Response({"message": "Email and Code are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            otp_record = OneTimePassword.objects.get(user=user)
        except (User.DoesNotExist, OneTimePassword.DoesNotExist):
            return Response({"message": "Invalid Email"}, status=status.HTTP_404_NOT_FOUND)
        
        if otp_record.is_blocked:
            return Response({
                "message": "This account is blocked due to multiple invalid attempts. Contact support."
            }, status=status.HTTP_403_FORBIDDEN)
        
        if otp_record.code == code:
            user.is_active = True
            user.save()
            otp_record.delete()
            return Response({"message": "Account verified successfully!"}, status=status.HTTP_200_OK)
        
        else:
            otp_record.attempts +=1
            otp_record.save()

            remaining_attempts = 3 - otp_record.attempts
            if remaining_attempts <= 0:
                otp_record.is_blocked=True
                otp_record.save()
                return Response({
                    "message": "Maximum attempts reached. Your account is now blocked."
                }, status=status.HTTP_403_FORBIDDEN)
            
            return Response({
                "message": f"Invalid code. You have {remaining_attempts} attempts left."
            }, status=status.HTTP_400_BAD_REQUEST)
        
class ResendOTPView(GenericAPIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            otp_record = OneTimePassword.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except OneTimePassword.DoesNotExist:
            # Agar user verified hai to OTP record nahi hoga
            return Response({"message": "User is already verified or invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.is_blocked:
             return Response({"message": "Account is blocked. Cannot resend code."}, status=status.HTTP_403_FORBIDDEN)

        # Naya code generate aur send karein
        send_otp_via_email(user)
        return Response({"message": "New code sent successfully."}, status=status.HTTP_200_OK)
    
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.failed_login_attempts >=3:
            if user.last_failed_time:
                current_time = timezone.now()
                lockout_time = user.last_failed_time + timedelta(minutes=15)

                if current_time < lockout_time:
                    remaining_time = (lockout_time - current_time).seconds//60
                    return Response({
                        "message": f"Your account is locked due to multiple failed attempts. Try again in {remaining_time + 1} minutes."
                    }, status=status.HTTP_403_FORBIDDEN)
                else:
                    user.failed_login_attempts = 0
                    user.last_failed_time = None
                    user.save()
        
        if not user.is_active:
            return Response({"message": "Account not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
        
        if user.check_password(password):
            user.failed_login_attempts = 0
            user.last_failed_time = None
            user.save()
            return Response({
                "message": "Login Successful",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_200_OK)
        
        else:
            user.failed_login_attempts += 1
            user.last_failed_time = timezone.now()
            user.save()
            
            attempts_left = 3 - user.failed_login_attempts

            if attempts_left <=0:
                return Response({
                    "message": "Maximum attempts reached. Account locked for 15 minutes."
                }, status=status.HTTP_403_FORBIDDEN)
            
            return Response({
                "message": f"Invalid password. You have {attempts_left} attempts left."
            }, status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                send_password_reset_otp(user)
                return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
                otp_record = OneTimePassword.objects.get(user=user)
            except (User.DoesNotExist, OneTimePassword.DoesNotExist):
                 return Response({"message": "Invalid request."}, status=status.HTTP_404_NOT_FOUND)
            
            if otp_record.is_blocked:
                return Response({"message": "Account blocked due to multiple attempts."}, status=status.HTTP_403_FORBIDDEN)
            
            if otp_record.code == otp:
                
                user.set_password(new_password) 
                user.save()
                otp_record.delete()
                send_password_success_email(user)
                
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            else:
                otp_record.attempts += 1
                otp_record.save()
                remaining = 3 - otp_record.attempts
                
                if remaining <= 0:
                    otp_record.is_blocked = True
                    otp_record.save()
                    return Response({"message": "Account blocked."}, status=status.HTTP_403_FORBIDDEN)
                
                return Response({"message": f"Invalid code. {remaining} attempts left."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
