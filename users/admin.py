from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile

# 内联管理 Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['email', 'username', 'age']
    model = CustomUser
    inlines = [ProfileInline]  # 添加内联
    
    # 重写get_inline_instances方法，确保在添加用户时不显示内联
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        try:
            if not obj.profile:
                Profile.objects.create(user=obj)
        except Profile.DoesNotExist:
            Profile.objects.create(user=obj)
        return super().get_inline_instances(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)

# 也可以单独注册Profile模型
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'work_area']
    search_fields = ['user__username', 'user__email']