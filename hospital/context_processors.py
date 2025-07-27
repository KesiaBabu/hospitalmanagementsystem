from django.utils.timezone import now
from hospital.models import Appointment, Consultation, PatientReassignment

def doctor_notification_counts(request):
    if request.user.is_authenticated and request.user.user_type == '2':  
        doctor = request.user

        consulted_appointment_ids = Consultation.objects.values_list('appointment_id', flat=True)

        new_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=now()
        ).exclude(id__in=consulted_appointment_ids)

       
        return {
            'new_appointments_count': new_appointments.count(),
        }

    return {
        'new_appointments_count': 0,
        
    }