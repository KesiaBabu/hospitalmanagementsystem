from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.validators import validate_email
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from hospital.models import CustomUser
from hospital.models import userdetails
from hospital.models import Department
from hospital.models import patient
from hospital.models import Appointment
from hospital.models import Consultation
from hospital.models import PatientReassignment
from datetime import datetime
from datetime import date
from django.utils.timezone import now
from django.http import JsonResponse
from django.utils import timezone
import random
import string
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Medicine
from .models import Bill, BillItem
from django.db import transaction

# Create your views here.
def home(request):
    return render(request,'home.html')

def loginpage(request):
    return render(request,'loginpage.html')

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('home')

def signup_doctor(request):
    department=Department.objects.all()
    return render(request,'doctor/signup_doctor.html',{'department':department})

def signup_pharmacy(request):
    return render(request,'pharmacy/signup_pharmacy.html')

@login_required
def reception_home(request):
    return render(request,'reception/reception_home.html')

def loginfun(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
             if user.user_type =='1':
                login(request, user)
                return redirect('reception_home')
             elif user.user_type =='2':    
                auth.login(request,user)
                messages.info(request, f'Welcome {username} !!')
                return redirect('doc_home')
             else:
                auth.login(request,user)
                messages.info(request, f'Welcome {username} !!')
                return redirect('pharmacy_home')
                 
        else:
            messages.info(request, 'Invalid Username or Password. Try Again')
            return redirect('loginpage') 
    else:
        messages.info(request, 'Invalid Username or Password. Try Again')
        return redirect('loginpage') 

@login_required   
def dept(request):
    return render(request,'reception/dept.html')

@login_required
def add_dept(request):
    if request.method=='POST':
        department_name = request.POST['department_name']
        description = request.POST['description']
        dept = Department(department_name=department_name, description=description)
        dept.save()
        return redirect('show_dept')

@login_required    
def show_dept(request):
    department = Department.objects.all()
    return render(request, 'reception/show_dept.html', {'department': department})

@login_required  
def delete_dept(request, id):
    dept = Department.objects.get(id=id)
    dept.delete()
    return redirect('show_dept')

def doc_reg(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        number = request.POST['number']
        image = request.FILES.get('image')
        user_type = request.POST['text']
        sel = request.POST['sel']
        department = Department.objects.get(id=sel)
        password = str(random.randint(100000, 999999))

        try:
            EmailValidator()(email)
        except ValidationError:
            messages.error(request, 'Invalid email format')
            return redirect('signup_doctor')
        if CustomUser.objects.filter(username=username).exists():
            messages.success(request, 'Username already exists !!')
            return redirect('signup_doctor')
        # elif CustomUser.objects.filter(email=email).exists():
        #     messages.success(request, 'Email already exists !!')
        #     return redirect('signup_doctor')
        else:
            user = CustomUser.objects.create_user(username=username,password=password,first_name=first_name, last_name=last_name, email=email, user_type=user_type)
            user.set_password(password)
            user.save()

            user_detail = userdetails(user=user, number=number, image=image, department=department)
            user_detail.save()

            subject = 'Thank you for registration'
            message = f'Hello {first_name},\n\nYour account has been created successfully.\n\nYour password: {password}\n\nThank you!'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, 'Password has been sent to your email. Please check your inbox.')
            return redirect('signup_doctor')

def pha_reg(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        number = request.POST['number']
        user_type = request.POST['text']
        
        password = str(random.randint(100000, 999999))

        try:
            EmailValidator()(email)
        except ValidationError:
            messages.error(request, 'Invalid email format')
            return redirect('signup_pharmacy')
        if CustomUser.objects.filter(username=username).exists():
            messages.success(request, 'Username already exists !!')
            return redirect('signup_pharmacy')
        elif CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'Email already exists !!')
            return redirect('signup_pharmacy')
        else:
            user = CustomUser.objects.create_user(username=username,password=password,first_name=first_name, last_name=last_name, email=email, user_type=user_type)
            user.set_password(password)
            user.save()

            user_detail = userdetails(user=user, number=number)
            user_detail.save()

            subject = 'Thank you for registration'
            message = f'Hello {first_name},\n\nYour account has been created successfully.\n\nYour password: {password}\n\nThank you!'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, 'Password has been sent to your email. Please check your inbox.')
            return redirect('signup_pharmacy')

@login_required      
def doc_home(request):
    
    current_doctor = request.user
    
    doctor_details = userdetails.objects.get(user=current_doctor)
    
    context = {
        'doctor': current_doctor,
        'doctor_details': doctor_details,
    }
    
    return render(request, 'doctor/doc_home.html', context)

def generate_patient_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

@login_required
def register_patient(request):
    if request.method == 'POST':
        patient_name = request.POST['pname']
        patient_address = request.POST['paddress']
        mobile_number = request.POST['pnumber']
        email = request.POST['email']
        patient_id = generate_patient_id()

        if not is_valid_email(email):
            messages.error(request, 'Invalid email address!')
            return redirect('register_patient')

        # if patient.objects.filter(email=email).exists():
        #     messages.success(request, 'Email already exists !!')
        #     return redirect('register_patient')
        else:
            pat = patient.objects.create(patient_name=patient_name, patient_address=patient_address, mobile_number=mobile_number, email=email, patient_id=patient_id)
            pat.save()
            subject = 'Patient Registered'
            message = f'Hello {patient_name},\n\nYour unique Patient ID: {patient_id}\n\nThank you for registering!'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return redirect('appointment_form',patient_id=pat.id)
        
    return render(request,'reception/register_patient.html')



@login_required
def appointment_form(request, patient_id):
    patient_instance = get_object_or_404(patient, id=patient_id)
    departments = Department.objects.all()
    doctors = CustomUser.objects.filter(userdetails__user__user_type=2)

    
    selected_department = request.GET.get('department')
    if selected_department:
        doctors = doctors.filter(Q(userdetails__department__id=selected_department, userdetails__isnull=False))
    print("Selected Department:", selected_department)
    print("Filtered Doctors:", doctors)

    if request.method == 'POST':
        department_id = request.POST.get('department')
        doctor_id = request.POST.get('doctor')
        appointment_date_str = request.POST.get('appointment_date')

        token_number = str(random.randint(100000, 999999))

        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')

        appointment = Appointment.objects.create(
            patient=patient_instance,
            department=Department.objects.get(pk=department_id),
            doctor=CustomUser.objects.get(pk=doctor_id),
            token_number=token_number,
            appointment_date=appointment_date
        )

        subject = 'Appointment Confirmation'
        message = f'Thank you for scheduling an appointment. Your token number is {token_number}.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [patient_instance.email])

        return render(request, 'reception/appointment_confirm.html', {'patient_id': patient_id, 'appointment': appointment, 'selected_department': selected_department})

    return render(request, 'reception/appointment_form.html', {'patient': patient_instance, 'departments': departments, 'doctors': doctors, 'selected_department': selected_department})


@login_required
def reassign_patient(request):
    current_doctor = request.user
    appointments = Appointment.objects.filter(doctor=current_doctor)
    departments = Department.objects.all()
    all_doctors = CustomUser.objects.filter(user_type='2')  # Only doctors

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        new_doctor_id = request.POST.get('new_doctor')
        reason = request.POST.get('reason')
        illness = request.POST.get('illness')
        medicine_name = request.POST.get('medicine_name')
        consumption_time = request.POST.get('consumption_time')
        department_id = request.POST.get('department')

        try:
            selected_patient = patient.objects.get(id=patient_id)
            new_doctor = CustomUser.objects.get(id=new_doctor_id)
            department = Department.objects.get(pk=department_id)

            reassignment = PatientReassignment.objects.create(
                patient=selected_patient,
                current_doctor=current_doctor,
                new_doctor=new_doctor,
                department=department,
                illness=illness,
                medicine_name=medicine_name,
                consumption_time=consumption_time,
                reassignment_date=timezone.now(),
                reason=reason
            )
            messages.success(request, "Patient reassigned successfully!")
            return redirect('reassign_patient')

        except patient.DoesNotExist:
            messages.error(request, "Selected patient does not exist.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Selected doctor does not exist.")
        except Department.DoesNotExist:
            messages.error(request, "Selected department does not exist.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

   
    selected_department = request.GET.get('department')
    doctors = CustomUser.objects.filter(user_type='2')
    if selected_department:
        doctors = doctors.filter(userdetails__department__id=selected_department)

   
    unique_patient_ids = set()
    unique_appointments = []
    for app in appointments:
        try:
            if app.patient and app.patient.id not in unique_patient_ids:
                unique_appointments.append(app)
                unique_patient_ids.add(app.patient.id)
        except Exception:
            continue

    return render(request, 'doctor/reassign_patient.html', {
        'appointments': unique_appointments,
        'all_doctors': all_doctors,
        'departments': departments,
        'doctors': doctors,
        'selected_department': selected_department
    })

@login_required  
def consult_reassigned_patient(request, reassignment_id):
    reassignment = get_object_or_404(PatientReassignment, id=reassignment_id, new_doctor=request.user)

    if request.method == 'POST':
        illness = request.POST.get('illness')
        medicine_name = request.POST.get('medicine_name')
        consumption_time = request.POST.get('consumption_time')

        
        appointment = Appointment.objects.create(
            patient=reassignment.patient,
            department=reassignment.department,
            doctor=request.user,
            token_number=str(reassignment.id) + "RS",
            appointment_date=timezone.now()
        )

        Consultation.objects.create(
            appointment=appointment,
            medicine_name=medicine_name,
            illness=illness,
            consumption_time=consumption_time
        )

       
        return redirect('reassigned_details')  

    return render(request, 'doctor/consult_reassigned_patient.html', {
        'reassignment': reassignment
    })


@login_required
def appointment_list(request):
    doctor = request.user
    appointments = Appointment.objects.filter(doctor=doctor, doctor__user_type='2').order_by('-appointment_date')

    context = {'appointments': appointments}
    return render(request, 'doctor/appointment_list.html', context)

@login_required
def consultation_form(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    context = {
        'appointment': appointment,
    }
    return render(request, 'doctor/consultation_form.html', context)

@login_required
def submit_consultation(request,appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        illness = request.POST.get('illness')
        medicine_name = request.POST.get('medicine_name')
        consumption_time = request.POST.get('consumption_time')
        

        consultation = Consultation.objects.create(
            appointment=appointment,
            medicine_name=medicine_name,
            illness=illness,
            consumption_time=consumption_time
        )
        consultation.save()

        messages.success(request, 'Consultation submitted successfully.')
        return redirect('appointment_list')  

    return render(request, 'doctor/consultation_form.html',{'appointment': appointment}) 

@login_required
def search_patient(request):
    if request.method == 'POST':
        doctor_user = request.user
        if doctor_user.user_type != '2':
            return redirect('search_patient')

        patient_id = request.POST.get('patient_id')

        
        patient_instance = patient.objects.filter(patient_id=patient_id).first()
        if not patient_instance:
            messages.error(request, 'No patient found with the specified ID.')
            return redirect('search_patient')

       
        appointments = Appointment.objects.filter(doctor=doctor_user, patient=patient_instance)
        if not appointments.exists():
            messages.warning(request, 'No appointments found for this patient with the current doctor.')
            return redirect('search_patient')

        consultations = Consultation.objects.filter(appointment__in=appointments)

        return render(request, 'doctor/search_result.html', {
            'patient': patient_instance,
            'consultations': consultations
        })

    return render(request, 'doctor/search_patient.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

     
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('change_password')

        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('change_password')

        if not any(char.isupper() for char in new_password1):
            messages.error(request, 'Password must contain at least one uppercase letter.')
            return redirect('change_password')

        if not any(char.islower() for char in new_password1):
            messages.error(request, 'Password must contain at least one lowercase letter.')
            return redirect('change_password')

        if not any(char.isdigit() for char in new_password1):
            messages.error(request, 'Password must contain at least one digit.')
            return redirect('change_password')

        if not any(char in string.punctuation for char in new_password1):
            messages.error(request, 'Password must contain at least one special character.')
            return redirect('change_password')

        
        request.user.set_password(new_password1)
        request.user.save()

       
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('change_password')

    return render(request, 'doctor/change_password.html')

@login_required
def r_search_result(request, patient_id):
    try:
        patient_instance = patient.objects.get(patient_id=patient_id)
    except patient.DoesNotExist:
        return render(request, 'reception/r_search_result.html', {'patient': None})

    now = timezone.now()

    all_appointments = Appointment.objects.filter(patient=patient_instance)
    consulted_ids = Consultation.objects.filter(appointment__in=all_appointments).values_list('appointment_id', flat=True)
    appointments = all_appointments.exclude(id__in=consulted_ids)
    upcoming_appointments = appointments.filter(appointment_date__gt=now)
    consultations = Consultation.objects.filter(appointment__in=all_appointments)

    return render(request, 'reception/r_search_result.html', {
        'patient': patient_instance,
        'consultations': consultations,
        'now': now,
        'appointments': appointments,  
        'upcoming_appointments': upcoming_appointments,
    })

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        if appointment.appointment_date > timezone.now():
            patient_id = appointment.patient.patient_id  # save before deleting
            appointment.delete()
            messages.success(request, "Appointment cancelled successfully.")
        else:
            messages.error(request, "Cannot cancel past appointments.")
            patient_id = appointment.patient.patient_id

    return redirect('r_search_result', patient_id=patient_id)

@login_required
def r_search_patient(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        return redirect('r_search_result', patient_id=patient_id)
    return render(request, 'reception/r_search_patient.html')




@login_required
def pharmacy_home(request):
    return render(request,'pharmacy/pharmacy_home.html')

@login_required
def p_change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        
        if not request.user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('p_change_password')

        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('p_change_password')

      
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('p_change_password')

        if not any(char.isupper() for char in new_password1):
            messages.error(request, 'Password must contain at least one uppercase letter.')
            return redirect('p_change_password')

        if not any(char.islower() for char in new_password1):
            messages.error(request, 'Password must contain at least one lowercase letter.')
            return redirect('p_change_password')

        if not any(char.isdigit() for char in new_password1):
            messages.error(request, 'Password must contain at least one digit.')
            return redirect('p_change_password')

        if not any(char in string.punctuation for char in new_password1):
            messages.error(request, 'Password must contain at least one special character.')
            return redirect('p_change_password')

       
        request.user.set_password(new_password1)
        request.user.save()

        
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('p_change_password')

    return render(request, 'pharmacy/p_change_password.html')


@login_required
def pres_details(request):
   
    consultations = Consultation.objects.all()

    context = {
        'consultations': consultations,
    }

    return render(request, 'pharmacy/pres_details.html', context)


from django.urls import reverse



@login_required
def appointment_details(request, patient_id):
    
    appointments = Appointment.objects.filter(patient__patient_id=patient_id)

    context = {
        'appointments': appointments,
    }

    return render(request, 'reception/appointment_details.html', context)


def reassign_patient_success(request):
    return render(request,'doctor/reassign_patient_success.html')

@login_required
def reassigned_details(request):
    current_doctor = request.user
    reassigned_patients = PatientReassignment.objects.filter(new_doctor=current_doctor)

    consulted_ids = set()
    for reassignment in reassigned_patients:
        token = str(reassignment.id) + "RS"
        if Appointment.objects.filter(token_number=token, consultation__isnull=False).exists():
            consulted_ids.add(reassignment.id)

    return render(request, 'doctor/reassigned_details.html', {
        'reassigned_patients': reassigned_patients,
        'consulted_ids': consulted_ids
    })

@login_required
def recent_prescriptions(request):
    recent_prescriptions = Consultation.objects.all().order_by('-timestamp')[:3] 

    return render(request, 'pharmacy/recent_prescriptions.html', {'recent_prescriptions': recent_prescriptions})



@login_required
def book_appointment(request):
    if request.method == 'POST':
        
        patient_id = request.POST['patient_id']
        department_id = request.POST['department']
        doctor_id = request.POST['doctor']
        # appointment_date = request.POST['appointment_date']
        appointment_date_str = request.POST['appointment_date']
        appointment_date = datetime.strptime(appointment_date_str, "%Y-%m-%dT%H:%M")
        appointment_date_only = appointment_date.date()

        try:
            patient_obj = patient.objects.get(patient_id=patient_id)
        except patient.DoesNotExist:
            messages.error(request, "Patient ID does not exist. Please enter a valid Patient ID.")
            return redirect('book_appointment')

        doctor = CustomUser.objects.get(pk=doctor_id)
        start = datetime.combine(appointment_date_only, datetime.min.time())
        end = datetime.combine(appointment_date_only, datetime.max.time())

        appointment_count = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__range=(start, end)
        ).count()

        if appointment_count >= 5:
            messages.error(request, "This doctor already has 5 appointments on the selected date. Please choose another date or doctor.")
            return redirect('book_appointment') 

       
        token_number = str(random.randint(100000, 999999))

        
        appointment = Appointment.objects.create(
            patient=patient.objects.get(patient_id=patient_id),
            department=Department.objects.get(pk=department_id),
            doctor=CustomUser.objects.get(pk=doctor_id),
            token_number=token_number,
            appointment_date=appointment_date
        )
        appointment.save()

        patient_email = patient.objects.get(patient_id=patient_id).email
        subject = 'Appointment Confirmation'
        message = f'Your appointment is confirmed. Token Number: {token_number}'
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [patient_email])

        return render(request, 'reception/appointment_details.html', {
            'patient_id': patient_id,
            'appointment': appointment
        })

    else:
        departments = Department.objects.all()
        selected_department = request.GET.get('department')
        
        
        selected_department_int = None
        if selected_department:
            try:
                selected_department_int = int(selected_department)
            except ValueError:
                selected_department_int = None

        doctors = CustomUser.objects.filter(user_type='2')
        if selected_department_int:
            doctors = doctors.filter(userdetails__department__id=selected_department_int)

        return render(request, 'reception/book_appointment.html', {
            'departments': departments,
            'doctors': doctors,
            'selected_department': selected_department_int
        })
    

    ##### Adding new Features #####

def forgot_password(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('forgot_password')

        try:
            user = CustomUser.objects.get(username=username_or_email)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found with that username or email.")
                return redirect('forgot_password')

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password reset successfully. Please login.")
        return redirect('loginpage')

    return render(request, 'forgot_password.html')

@login_required
def download_consultation_summary(request, consultation_id):
    consultation = Consultation.objects.get(id=consultation_id)
    template = get_template('reception/consultation_pdf.html')
    html = template.render({'consultation': consultation})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="consultation_{consultation.id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response

@login_required
def doctor_schedule_view(request):
    selected_date = request.GET.get('date', date.today().isoformat())  
    
 
    doctors = CustomUser.objects.filter(user_type='2')  

    schedule = []
    for doctor in doctors:
        appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=selected_date
        ).order_by('appointment_date')

        schedule.append({
            'doctor': doctor,
            'department': doctor.userdetails.department.department_name if hasattr(doctor, 'userdetails') else 'N/A',
            'appointments': appointments
        })

    return render(request, 'reception/doctor_schedule.html', {
        'schedule': schedule,
        'selected_date': selected_date
    })

@login_required
def doctor_schedule(request):
    departments = Department.objects.all()
    selected_department = request.POST.get("department")
    selected_doctor = request.POST.get("doctor")
    selected_date_str = request.POST.get("appointment_date")

    doctors = CustomUser.objects.filter(user_type='2', userdetails__department__id=selected_department) if selected_department else []
    appointments = []
    selected_doctor_obj = None
    selected_date = None
    available_slots = None 

    if selected_doctor and selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        selected_doctor_obj = CustomUser.objects.get(id=selected_doctor)

        start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))

        appointments = Appointment.objects.filter(
            doctor=selected_doctor_obj,
            appointment_date__range=(start_datetime, end_datetime)
        )
        max_slots = 5
        available_slots = max_slots - appointments.count()

    context = {
        "departments": departments,
        "doctors": doctors,
        "appointments": appointments,
        "selected_department": selected_department,
        "selected_doctor": selected_doctor_obj,
        "selected_date": selected_date_str,
        "available_slots": available_slots  
    }
    return render(request, "reception/doctor_schedule.html", context)

def get_doctors_by_department(request):
    dept_id = request.GET.get("dept_id")
    doctors = []
    if dept_id:
        doctors_qs = CustomUser.objects.filter(
            userdetails__department__id=dept_id,
            user_type='2'  # assuming '2' means doctor
        ).distinct()
        doctors = [{"id": doc.id, "name": doc.get_full_name()} for doc in doctors_qs]
    return JsonResponse({"doctors": doctors})

@login_required
def stock_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'pharmacy/stock_list.html', {'medicines': medicines})

@login_required
def add_medicine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        expiry_date = request.POST.get('expiry_date')

        if not Medicine.objects.filter(name=name).exists():
            Medicine.objects.create(
                name=name,
                description=description,
                quantity=quantity,
                price=price,
                expiry_date=expiry_date
            )
            messages.success(request, 'Medicine added successfully.')
            return redirect('stock_list')
        else:
            messages.error(request, 'Medicine with this name already exists.')
    
    return render(request, 'pharmacy/add_medicine.html')

@login_required
def create_bill(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient')
        medicine_ids = request.POST.getlist('medicine[]')
        quantities = request.POST.getlist('quantity[]')

        patient_obj = patient.objects.get(id=patient_id)
        total_amount = 0
        bill = Bill.objects.create(patient=patient_obj, total_amount=0) 

        for med_id, qty in zip(medicine_ids, quantities):
            medicine = Medicine.objects.get(id=med_id)
            qty = int(qty)

            if medicine.quantity < qty:
                messages.error(request, f"Not enough stock for {medicine.name}")
                bill.delete()
                return redirect('create_bill')

            subtotal = medicine.price * qty
            total_amount += subtotal

            BillItem.objects.create(
                bill=bill,
                medicine=medicine,
                quantity=qty,
                price=medicine.price
            )

            medicine.quantity -= qty
            medicine.save()

        bill.total_amount = total_amount
        bill.save()
        return redirect('bill_detail', bill.id)

    patients = patient.objects.all()
    medicines = Medicine.objects.all()
    return render(request, 'pharmacy/create_bill.html', {
        'patients': patients,
        'medicines': medicines
    })

@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = BillItem.objects.filter(bill=bill)

    
    for item in items:
        item.subtotal = item.price * item.quantity

    return render(request, 'pharmacy/bill_detail.html', {
        'bill': bill,
        'items': items,
    })

def download_bill_pdf(request, bill_id):
    bill = Bill.objects.get(id=bill_id)
    items = BillItem.objects.filter(bill=bill)
    for item in items:
        item.subtotal = item.price * item.quantity


    template_path = 'pharmacy/bill_pdf.html'
    context = {
        'bill': bill,
        'items': items,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bill_{bill.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response

@login_required
def edit_medicine(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    if request.method == 'POST':
        medicine.name = request.POST.get('name')
        medicine.description = request.POST.get('description')
        medicine.quantity = request.POST.get('quantity')
        medicine.price = request.POST.get('price')
        medicine.expiry_date = request.POST.get('expiry_date')
        medicine.save()
        messages.success(request, "Medicine updated successfully!")
        return redirect('stock_list')
    return render(request, 'pharmacy/edit_medicine.html', {'medicine': medicine})

def delete_medicine(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    medicine.delete()
    messages.warning(request, "Medicine deleted.")
    return redirect('stock_list')

@login_required
def search_patient_billing(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        try:
            pat = patient.objects.get(patient_id=patient_id)
            bills = Bill.objects.filter(patient=pat).prefetch_related('items__medicine')
            for bill in bills:
                for item in bill.items.all():
                    item.subtotal = item.quantity * item.price
            
            return render(request, "pharmacy/pha_search.html", {"patient": pat, "bills": bills})
        except patient.DoesNotExist:
            messages.error(request, "Patient ID not found.")

    return render(request, "pharmacy/p_search_patient.html")

@login_required
def doctor_notifications(request):
    doctor = request.user
    consulted_appointment_ids = Consultation.objects.values_list('appointment_id', flat=True)

    new_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=now()
    ).exclude(id__in=consulted_appointment_ids)

    
    return render(request, 'doctor/notifications.html', {
        'new_appointments': new_appointments,
        'new_appointments_count': new_appointments.count(),
    })