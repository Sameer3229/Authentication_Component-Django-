
from django.urls import path
from .views import SignupView, VerifyOTPView, ResendOTPView, LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyOTPView.as_view(), name='verify-email'),
    path('resend-code/', ResendOTPView.as_view(), name='resend-code'),
    path('login/', LoginView.as_view(), name='login')
]