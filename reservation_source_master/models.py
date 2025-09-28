from django.db import models
import uuid
from discount_master.models import DiscountMaster

class ReservationSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('OTA', 'Online Travel Agency'),
        ('DIRECT', 'Direct Booking'),
        ('CORPORATE', 'Corporate'),
        ('TRAVEL_AGENT', 'Travel Agent'),
        ('OTHER', 'Other')
    ]
    
    source_id = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    website_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    available_discounts = models.ManyToManyField(DiscountMaster, blank=True, related_name='reservation_sources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.source_id:
            # Generate a unique source ID
            self.source_id = f"RS{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def get_applicable_discounts(self):
        """Get all active discounts available for this reservation source"""
        return self.available_discounts.all()
    
    def can_apply_discount(self, discount_id):
        """Check if a specific discount can be applied for this reservation source"""
        return self.available_discounts.filter(discount_id=discount_id).exists()
    
    def calculate_discount_amount(self, base_amount, discount_id):
        """Calculate discount amount for a given base amount and discount"""
        try:
            discount = self.available_discounts.get(discount_id=discount_id)
            if discount.discount_value.endswith('%'):
                percent = float(discount.discount_value.rstrip('%'))
                return base_amount * (percent / 100)
            else:
                return float(discount.discount_value)
        except:
            return 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Reservation Source"
        verbose_name_plural = "Reservation Sources"
        ordering = ['name']
