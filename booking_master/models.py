from django.db import models
from rooms.models import RoomType
from reservation_source_master.models import ReservationSource

class Booking(models.Model):
    ID_PROOF_CHOICES = [
        ('AADHAR', 'Aadhar Card'),
        ('PAN', 'PAN Card'),
        ('DRIVING_LICENCE', 'Driving Licence'),
        ('OTHER', 'Other'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('OTHER', 'Other'),
    ]

    booking_id = models.AutoField(primary_key=True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    id_number = models.CharField(max_length=50)
    id_photo = models.ImageField(upload_to='guest_id_proofs/')
    booking_date = models.DateField(auto_now_add=True)
    booking_time = models.TimeField(auto_now_add=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    reservation_source = models.ForeignKey(ReservationSource, on_delete=models.SET_NULL, null=True, blank=True, help_text="Source of this booking")
    applied_discounts = models.ManyToManyField('discount_master.DiscountMaster', blank=True, help_text="Discounts applied to this booking")
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Base booking amount before discounts")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total discount amount")
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Final amount after discounts")
    reservation_source = models.ForeignKey(ReservationSource, on_delete=models.PROTECT)

    def calculate_discounts(self):
        """Calculate total discount amount based on applied discounts"""
        total_discount = 0
        for discount in self.applied_discounts.all():
            if discount.discount_value.endswith('%'):
                percent = float(discount.discount_value.rstrip('%'))
                total_discount += self.base_amount * (percent / 100)
            else:
                total_discount += float(discount.discount_value)
        return total_discount
    
    def update_final_amount(self):
        """Update final amount after calculating discounts"""
        self.discount_amount = self.calculate_discounts()
        self.final_amount = self.base_amount - self.discount_amount
        if self.final_amount < 0:
            self.final_amount = 0
    
    def get_available_discounts(self):
        """Get available discounts from reservation source"""
        if self.reservation_source:
            return self.reservation_source.get_applicable_discounts()
        return []
    
    def save(self, *args, **kwargs):
        # Calculate final amount before saving
        if self.base_amount > 0:
            self.update_final_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_first_name} {self.customer_last_name}"
