from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile

# 為 CustomUser 創建 Resource 類別 - 包含所有欄位
class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['email']  # 使用 email 作為唯一識別
        exclude = ('password',)  # 排除密碼欄位
        export_order = ('id', 'email', 'username', 'age', 'is_staff', 'is_active', 'date_joined', 'last_login')

    # 如果需要處理密碼，可以覆寫此方法
    def before_import_row(self, row, **kwargs):
        # 這裡可以處理密碼等敏感資料
        pass

# 為 Profile 創建 Resource 類別 - 包含所有欄位
class ProfileResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, 'email')  # 使用 email 關聯用戶
    )
    
    class Meta:
        model = Profile
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['user']  # 使用 user 作為唯一識別
        export_order = ('id', 'user', 'role', 'work_area', 'created_at', 'updated_at')

# 內聯管理 Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    extra = 0  # 不顯示額外的空白表單
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['email', 'username', 'age', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['email']
    model = CustomUser
    inlines = [ProfileInline]
    resource_class = CustomUserResource
    
    # 定義匯出/匯入的欄位集
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('age',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'age', 'password1', 'password2'),
        }),
    )
    
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

# 單獨註冊Profile模型並添加完整匯入/匯出功能
@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    list_display = ['user', 'role', 'work_area', 'created_at', 'updated_at']
    list_filter = ['role', 'work_area']
    search_fields = ['user__email', 'user__username', 'work_area']
    resource_class = ProfileResource
    
    # 修正後的 fieldsets，移除非可編輯欄位
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Profile Info', {'fields': ('role', 'work_area')}),
        # 移除了包含 created_at 和 updated_at 的部分
    )
    
    # 如果需要顯示這些欄位但不允許編輯，可以使用 readonly_fields
    readonly_fields = ('created_at', 'updated_at')