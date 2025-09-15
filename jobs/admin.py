from django.contrib import admin
from .models import Category, Job, JobImage, JobApplication, Review


class JobImageInline(admin.TabularInline):
    model = JobImage
    extra = 1
    readonly_fields = ('uploaded_at',)


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('fundi', 'proposed_rate', 'status', 'created_at', 'message')


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'category', 'status', 'urgency', 'budget_min', 'budget_max', 'created_at')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('title', 'customer__email', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Job Details', {
            'fields': ('title', 'customer', 'category', 'description', 'location')
        }),
        ('Budget & Deadline', {
            'fields': ('budget_min', 'budget_max', 'urgency', 'deadline')
        }),
        ('Status', {
            'fields': ('status', 'fundi')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [JobImageInline, JobApplicationInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'fundi', 'status', 'proposed_rate', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'fundi__user__email', 'fundi__user__first_name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'fundi', 'message', 'proposed_rate')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('job__title', 'reviewer__email', 'reviewee__email')
    readonly_fields = ('created_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(Review, ReviewAdmin)

# Customize admin site header and title
admin.site.site_header = "FundiConnect Admin"
admin.site.site_title = "FundiConnect Admin Portal"
admin.site.index_title = "Welcome to FundiConnect Administration"
