from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FundiProfile, PortfolioImage


class FundiProfileInline(admin.StackedInline):
    model = FundiProfile
    can_delete = False
    verbose_name_plural = 'Fundi Profile'
    extra = 0


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    readonly_fields = ('uploaded_at',)


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_verified', 'onboarding_complete', 'date_joined')
    list_filter = ('role', 'is_verified', 'onboarding_complete', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('FundiConnect Info', {
            'fields': ('role', 'phone_number', 'location', 'is_verified', 'onboarding_complete')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('FundiConnect Info', {
            'fields': ('email', 'role', 'phone_number', 'location')
        }),
    )
    
    inlines = [FundiProfileInline]


class FundiProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability', 'rating', 'total_jobs_completed', 'hourly_rate')
    list_filter = ('availability', 'rating', 'experience_years')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'skills')
    readonly_fields = ('rating', 'total_jobs_completed')
    
    inlines = [PortfolioImageInline]


class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('fundi', 'title', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('fundi__user__email', 'title', 'description')


admin.site.register(User, UserAdmin)
admin.site.register(FundiProfile, FundiProfileAdmin)
admin.site.register(PortfolioImage, PortfolioImageAdmin)
