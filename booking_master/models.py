from django.db import models
from decimal import Decimal
from rooms.models import RoomType
from reservation_source_master.models import ReservationSource
from timeslotmaster.models import TimeslotMaster
from discount_master.models import DiscountMaster

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
    booking_date = models.DateField(verbose_name="Booking Date")
    booking_time = models.TimeField(verbose_name="Booking Time")
    gst_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Customer GST Number")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeslotMaster, on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    reservation_source = models.ForeignKey(ReservationSource, on_delete=models.PROTECT)
    applied_discount = models.ForeignKey(DiscountMaster, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Applied Discount")
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Base Amount")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Discount Amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Amount")

    def calculate_amounts(self):
        """Calculate base amount, discount amount, and total amount"""
        from rate.models import RatePlan
        from decimal import Decimal
        
        # Get base amount from rate plan
        try:
            rate_plan = RatePlan.objects.filter(
                room_type=self.room_type,
                time_slot=self.time_slot,
                is_active=True
            ).first()
            
            if rate_plan:
                self.base_amount = rate_plan.base_rate
            else:
                self.base_amount = Decimal('0.00')
        except:
            self.base_amount = Decimal('0.00')
        
        # Calculate discount amount
        if self.applied_discount:
            try:
                if self.applied_discount.discount_value.endswith('%'):
                    # Percentage discount
                    percent = Decimal(self.applied_discount.discount_value.rstrip('%'))
                    self.discount_amount = self.base_amount * (percent / Decimal('100'))
                else:
                    # Fixed amount discount
                    self.discount_amount = Decimal(str(self.applied_discount.discount_value))
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error calculating discount: {e}")
                self.discount_amount = Decimal('0.00')
        else:
            self.discount_amount = Decimal('0.00')
        
        # Calculate total amount
        self.total_amount = self.base_amount - self.discount_amount
        if self.total_amount < Decimal('0.00'):
            self.total_amount = Decimal('0.00')

    def save(self, *args, **kwargs):
        # Calculate amounts before saving
        self.calculate_amounts()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_first_name} {self.customer_last_name}"