from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import BookingForm
from rate.models import RatePlan
from timeslotmaster.models import TimeslotMaster
from rooms.models import RoomType
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Booking
from .forms import BookingForm

def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'booking_master/booking_form.html', {'form': form})


# AJAX endpoint to get time slots for a room type
def get_time_slots(request):
    room_type_id = request.GET.get('room_type_id')
    time_slots = []
    if room_type_id:
        try:
            # Get unique time_slot ids for this room_type from RatePlan
            slot_ids = list(RatePlan.objects.filter(room_type_id=room_type_id, is_active=True)
                            .values_list('time_slot', flat=True).distinct())
            print(f"Found slot_ids for room_type {room_type_id}: {slot_ids}")
            
            # Remove duplicates by using set
            unique_slots = TimeslotMaster.objects.filter(id__in=set(slot_ids)).order_by('name')
            print(f"Found unique_slots: {list(unique_slots)}")
            
            time_slots = [{'id': slot.id, 'name': slot.name, 'time': slot.time} for slot in unique_slots]
            print(f"Returning time_slots: {time_slots}")
        except Exception as e:
            print(f"Error in get_time_slots: {e}")
    
    return JsonResponse({'time_slots': time_slots})

# AJAX endpoint to get price for room type and time slot
def get_price(request):
    room_type_id = request.GET.get('room_type_id')
    time_slot_id = request.GET.get('time_slot_id')
    price = None
    if room_type_id and time_slot_id:
        rate = RatePlan.objects.filter(room_type_id=room_type_id, time_slot_id=time_slot_id, is_active=True).order_by('base_rate').first()
        if rate:
            price = str(rate.base_rate)
    return JsonResponse({'price': price})

def booking_success(request):
    return render(request, 'booking_master/booking_success.html')

# AJAX endpoint to get commission_rate for reservation_source
from reservation_source_master.models import ReservationSource

def get_commission_rate(request):
    source_id = request.GET.get('reservation_source_id')
    commission_rate = 0
    if source_id:
        try:
            source = ReservationSource.objects.get(id=source_id)
            commission_rate = float(source.commission_rate)
        except ReservationSource.DoesNotExist:
            commission_rate = 0
    return JsonResponse({'commission_rate': commission_rate})

# AJAX endpoint to get available discounts for reservation_source
def get_available_discounts(request):
    source_id = request.GET.get('reservation_source_id')
    discounts = []
    if source_id:
        try:
            source = ReservationSource.objects.get(id=source_id)
            for discount in source.available_discounts.all():
                discounts.append({
                    'id': discount.discount_id,
                    'description': discount.description,
                    'discount_value': discount.discount_value
                })
        except ReservationSource.DoesNotExist:
            pass
    return JsonResponse({'discounts': discounts})

class BookingListView(ListView):
    model = Booking
    template_name = 'booking_master/booking_list.html'
    context_object_name = 'bookings'
    ordering = ['-booking_date']

class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_master/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingDetailView(DetailView):
    model = Booking
    template_name = 'booking_master/booking_detail.html'
    context_object_name = 'booking'

class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_master/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingDeleteView(DeleteView):
    model = Booking
    template_name = 'booking_master/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')
    context_object_name = 'booking'
