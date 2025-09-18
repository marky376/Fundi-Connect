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
    list_display = ('email', 'username', 'active_role', 'display_roles', 'is_verified', 'onboarding_complete', 'date_joined')
    list_filter = ('active_role', 'is_verified', 'onboarding_complete', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('FundiConnect Info', {
            'fields': ('active_role', 'roles', 'phone_number', 'location', 'is_verified', 'onboarding_complete')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('FundiConnect Info', {
            'fields': ('email', 'active_role', 'roles', 'phone_number', 'location')
        }),
    )
    
    inlines = [FundiProfileInline]

    def display_roles(self, obj):
        return ', '.join(obj.roles) if obj.roles else ''
    display_roles.short_description = 'Roles'


class FundiProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability', 'rating', 'total_jobs_completed', 'hourly_rate', 'verification_status', 'verified_at')
    list_filter = ('availability', 'rating', 'experience_years', 'verification_status')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'skills')
    readonly_fields = ('rating', 'total_jobs_completed', 'verified_at')
    inlines = [PortfolioImageInline]
    fields = ('user', 'skills', 'description', 'experience_years', 'hourly_rate', 'availability', 'rating', 'total_jobs_completed', 'latitude', 'longitude', 'profile_photo', 'id_document', 'verification_status', 'verification_comment', 'verified_at')

    def approve_verification(self, request, queryset):
        updated = queryset.update(verification_status='approved')
        self.message_user(request, f"{updated} fundi profiles approved.")
    approve_verification.short_description = "Approve selected fundi verification"

    def reject_verification(self, request, queryset):
        updated = queryset.update(verification_status='rejected')
        self.message_user(request, f"{updated} fundi profiles rejected.")
    reject_verification.short_description = "Reject selected fundi verification"

    actions = ['approve_verification', 'reject_verification']


class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('fundi', 'title', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('fundi__user__email', 'title', 'description')


admin.site.register(User, UserAdmin)
admin.site.register(FundiProfile, FundiProfileAdmin)
admin.site.register(PortfolioImage, PortfolioImageAdmin)
