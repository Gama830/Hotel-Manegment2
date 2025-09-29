from django.contrib import admin
from .models import ReservationSource

@admin.register(ReservationSource)
class ReservationSourceAdmin(admin.ModelAdmin):
    list_display = ['source_id', 'name', 'source_type', 'contact_person', 'commission_rate', 'discount_count', 'is_active', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at', 'available_discounts']
    search_fields = ['name', 'source_id', 'contact_person', 'email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['available_discounts']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_id', 'name', 'source_type', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'email', 'phone', 'address', 'website_url')
        }),
        ('Business Details', {
            'fields': ('commission_rate', 'notes')
        }),
        ('Discounts', {
            'fields': ('available_discounts',),
            'description': 'Select multiple discounts that can be applied to bookings from this source'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_count(self, obj):
        return obj.available_discounts.count()
    discount_count.short_description = 'Discounts'