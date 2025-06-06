from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView


class SignUp(generic.CreateView):
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('login')
	template_name = 'signup.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')  # 確保這裡指向正確的URL名稱


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # 設定登出後跳轉到登入頁面