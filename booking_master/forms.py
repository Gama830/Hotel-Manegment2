from django import forms
from .models import Booking
from timeslotmaster.models import TimeslotMaster
from rate.models import RatePlan
from rooms.models import RoomType
from discount_master.models import DiscountMaster

class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label='Booking Date'
    )
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=True,
        label='Booking Time'
    )
    gst_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer GST Number'}),
        required=False,
        label='Customer GST Number'
    )
    time_slot = forms.ModelChoiceField(
        queryset=TimeslotMaster.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Time Slot'
    )
    applied_discount = forms.ModelChoiceField(
        queryset=DiscountMaster.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'calculateTotal();'}),
        label='Applied Discount',
        empty_label="No discount"
    )
    base_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        label='Base Amount'
    )
    discount_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        label='Discount Amount'
    )
    total_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        label='Total Amount'
    )

    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'customer_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'customer_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'id_proof_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID Number'
            }),
            'id_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'updateTimeSlotsAndPrice();'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reservation_source': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_reservation_source',
                'onchange': 'updateAvailableDiscounts();'
            }),
            # booking_date, booking_time, gst_number, applied_discount handled above
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle time slot queryset
        if 'room_type' in self.data:
            try:
                room_type_id = int(self.data.get('room_type'))
                self.fields['time_slot'].queryset = RatePlan.objects.filter(room_type_id=room_type_id).values_list('time_slot', flat=True).distinct()
                self.fields['time_slot'].queryset = TimeslotMaster.objects.filter(id__in=self.fields['time_slot'].queryset)
            except (ValueError, TypeError):
                self.fields['time_slot'].queryset = TimeslotMaster.objects.none()
        elif self.instance.pk:
            self.fields['time_slot'].queryset = TimeslotMaster.objects.filter(rate_plans__room_type=self.instance.room_type).distinct()
        else:
            self.fields['time_slot'].queryset = TimeslotMaster.objects.none()
        
        # Handle discount queryset
        if 'reservation_source' in self.data:
            try:
                source_id = int(self.data.get('reservation_source'))
                from reservation_source_master.models import ReservationSource
                source = ReservationSource.objects.get(id=source_id)
                self.fields['applied_discount'].queryset = source.available_discounts.all()
            except (ValueError, TypeError, ReservationSource.DoesNotExist):
                self.fields['applied_discount'].queryset = DiscountMaster.objects.none()
        elif self.instance.pk and self.instance.reservation_source:
            self.fields['applied_discount'].queryset = self.instance.reservation_source.available_discounts.all()
        else:
            self.fields['applied_discount'].queryset = DiscountMaster.objects.none()
