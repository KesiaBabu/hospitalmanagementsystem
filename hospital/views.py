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
import random
import string

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
        elif CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'Email already exists !!')
            return redirect('signup_doctor')
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

        if patient.objects.filter(email=email).exists():
            messages.success(request, 'Email already exists !!')
            return redirect('register_patient')
        else:
            pat = patient.objects.create(patient_name=patient_name, patient_address=patient_address, mobile_number=mobile_number, email=email, patient_id=patient_id)
            pat.save()
            subject = 'Patient Registered'
            message = f'Hello {patient_name},\n\nYour unique Patient ID: {patient_id}\n\nThank you for registering!'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return redirect('appointment_form',patient_id=pat.id)
        
    return render(request,'reception/register_patient.html')

from django.utils import timezone

# def appointment_form(request, patient_id):
#     patient_instance = get_object_or_404(patient, id=patient_id)
#     departments = Department.objects.all()
#     doctors = CustomUser.objects.filter(userdetails__user__user_type=2)

#     if request.method == 'POST':
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')
#         appointment_date_str = request.POST.get('appointment_date')  

#         selected_department = Department.objects.get(id=department_id)
#         selected_doctor = get_object_or_404(CustomUser, id=doctor_id)
#         token_number = str(random.randint(100000, 999999))

#        
#         appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')

#         appointment = Appointment.objects.create(
#             patient=patient_instance,
#             department=selected_department,
#             doctor=selected_doctor,
#             token_number=token_number,
#             appointment_date=appointment_date
#         )
#         subject = 'Appointment Confirmation'
#         message = f'Thank you for scheduling an appointment. Your token number is {token_number}.'
#         send_mail(subject, message, settings.EMAIL_HOST_USER, [patient_instance.email])

#        
#         return render(request, 'reception/appointment_confirm.html', {'patient_id': patient_id, 'appointment_id': appointment.id})

#     return render(request, 'reception/appointment_form.html', {'patient': patient_instance, 'departments': departments, 'doctors': doctors})

# def appointment_form(request, patient_id):
#     patient_instance = get_object_or_404(patient, id=patient_id)
#     departments = Department.objects.all()
#     doctors = CustomUser.objects.filter(userdetails__user__user_type=2)

#     if request.method == 'POST':
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')
#         appointment_date_str = request.POST.get('appointment_date')  

        
#         token_number = str(random.randint(100000, 999999))

#         
#         appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')

#       
#         appointment = Appointment.objects.create(
#             patient=patient_instance,
#             department=Department.objects.get(pk=department_id),
#             doctor=CustomUser.objects.get(pk=doctor_id),
#             # doctor=doctor_id,
#             token_number=token_number,
#             appointment_date=appointment_date
#         )
#         subject = 'Appointment Confirmation'
#         message = f'Thank you for scheduling an appointment. Your token number is {token_number}.'
#         send_mail(subject, message, settings.EMAIL_HOST_USER, [patient_instance.email])

#         
#         return render(request, 'reception/appointment_confirm.html', {'patient_id': patient_id, 'appointment': appointment})
#     else:  # GET request
#         
#         selected_department = request.GET.get('department')
#         doctors = CustomUser.objects.filter(user_type='2')

#         
#         if selected_department:
#             doctors = CustomUser.objects.filter(Q(userdetails__department__id=selected_department))

#     return render(request, 'reception/appointment_form.html', {'patient': patient_instance, 'departments': departments, 'doctors': doctors})

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
# def reassign_patient(request):
#     current_doctor = request.user
#     appointments = Appointment.objects.filter(doctor=current_doctor)
#     departments=Department.objects.all()
    

#     if request.method == 'POST':
#         department_id = request.POST['department']
#         patient_id = request.POST.get('patient')
#         new_doctor_id = request.POST.get('new_doctor')
#         reason = request.POST.get('reason')
#         illness = request.POST.get('illness')
#         medicine_name = request.POST.get('medicine_name')
#         consumption_time = request.POST.get('consumption_time')

#         patient_instance = patient.objects.get(id=patient_id)
#         new_doctor = CustomUser.objects.get(id=new_doctor_id)

#         
#         PatientReassignment.objects.create(
#             department=Department.objects.get(pk=department_id),
#             patient=patient_instance,
#             current_doctor=current_doctor,
#             new_doctor=CustomUser.objects.get(pk=new_doctor),
#             illness=illness,
#             medicine_name=medicine_name,
#             consumption_time=consumption_time,
#             reassignment_date=timezone.now(),
#             reason=reason
#         )

#         
#         return redirect('reassign_patient')
#     else:  # GET request
#         departments = Department.objects.all()
#         selected_department = request.GET.get('department')
#         doctors = CustomUser.objects.filter(user_type='2')

#         # Filter doctors based on the selected department if a department is selected
#         if selected_department:
#             doctors = CustomUser.objects.filter(Q(userdetails__department__id=selected_department))

#     return render(request, 'doctor/reassign_patient.html', {'appointments': appointments,  'current_doctor': current_doctor,'departments': departments, 'doctors': doctors, 'selected_department': selected_department})
####################################################correct one down#####################################3

# def reassign_patient(request):
#     current_doctor = request.user
#     appointments = Appointment.objects.filter(doctor=current_doctor)
#     all_doctors = CustomUser.objects.filter(userdetails__user__user_type=2)
#     departments = Department.objects.all()  

#     if request.method == 'POST':
#         patient_id = request.POST.get('patient')
#         new_doctor_id = request.POST.get('new_doctor')
#         reason = request.POST.get('reason')
#         illness = request.POST.get('illness')
#         medicine_name = request.POST.get('medicine_name')
#         consumption_time = request.POST.get('consumption_time')
#         department_id = request.POST.get('department')

#         patient_instance = patient.objects.get(id=patient_id)
#         new_doctor = CustomUser.objects.get(id=new_doctor_id)

#         
#         PatientReassignment.objects.create(
#             department=Department.objects.get(pk=department_id),
#             patient=patient_instance,
#             current_doctor=current_doctor,
#             new_doctor=new_doctor,
#             illness=illness,
#             medicine_name=medicine_name,
#             consumption_time=consumption_time,
#             reassignment_date=timezone.now(),
#             reason=reason
#         )

#        
#         return redirect('reassign_patient')

#     else:  
        
#         selected_department = request.GET.get('department')
#         doctors = CustomUser.objects.filter(user_type='2')

#         # Filter doctors based on the selected department if a department is selected
#         if selected_department:
#             doctors = CustomUser.objects.filter(Q(userdetails__department__id=selected_department))

#     return render(request, 'doctor/reassign_patient.html', {'appointments': appointments, 'all_doctors': all_doctors, 'current_doctor': current_doctor, 'departments': departments, 'doctors': doctors, 'selected_department': selected_department})

@login_required
def reassign_patient(request):
    current_doctor = request.user
    appointments = Appointment.objects.filter(doctor=current_doctor)
    all_doctors = CustomUser.objects.filter(userdetails__user__user_type=2)
    departments = Department.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        new_doctor_id = request.POST.get('new_doctor')
        reason = request.POST.get('reason')
        illness = request.POST.get('illness')
        medicine_name = request.POST.get('medicine_name')
        consumption_time = request.POST.get('consumption_time')
        department_id = request.POST.get('department')
        appointment_date_str = request.POST.get('appointment_date')

        patient_instance = patient.objects.get(id=patient_id)
        new_doctor = CustomUser.objects.get(id=new_doctor_id)

        
        reassignment_instance = PatientReassignment.objects.create(
            department=Department.objects.get(pk=department_id),
            patient=patient_instance,
            current_doctor=current_doctor,
            new_doctor=new_doctor,
            illness=illness,
            medicine_name=medicine_name,
            consumption_time=consumption_time,
            reassignment_date=timezone.now(),
            reason=reason
        )
        token_number = str(random.randint(100000, 999999))
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
       
        Appointment.objects.create(
            patient=patient_instance,
            department=reassignment_instance.department,
            doctor=new_doctor,
            token_number=token_number,  
            appointment_date=appointment_date  
        )
        subject = 'Appointment Confirmation'
        message = f'Thank you for scheduling an appointment. Your token number is {token_number}.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [patient_instance.email])
        messages.success(request, 'Patient reassigned successfully!!')
        return redirect('reassign_patient')

    else:  # GET request
        selected_department = request.GET.get('department')
        doctors = CustomUser.objects.filter(user_type='2')

        if selected_department:
            doctors = CustomUser.objects.filter(Q(userdetails__department__id=selected_department))

    return render(request, 'doctor/reassign_patient.html', {'appointments': appointments, 'all_doctors': all_doctors, 'current_doctor': current_doctor, 'departments': departments, 'doctors': doctors, 'selected_department': selected_department})   

# def appointment_confirm(request, patient_id, appointment_id):
#     
#     patient_instance = patient.objects.get(id=patient_id)
#     appointment_instance = Appointment.objects.get(id=appointment_id)

#     
#     context = {
#         'patient': patient_instance,
#         'appointment': appointment_instance,
#     }

#     
#     return render(request, 'reception/appointment_confirm.html', context)
    


@login_required
def appointment_list(request):
    # Sorting the appointments by appointment_date
    # appointments = Appointment.objects.all().order_by('-appointment_date')
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

# def search_patient(request):
#     if request.method == 'POST':
#         patient_id = request.POST.get('patient_id')
#         patient_instance = get_object_or_404(patient, patient_id=patient_id)
        
#         # Retrieve all appointments related to the patient
#         appointments = Appointment.objects.filter(patient=patient_instance)
        
#         # Retrieve all consultations related to the patient's appointments
#         consultations = Consultation.objects.filter(appointment__in=appointments)

#         return render(request, 'doctor/search_result.html', {'patient': patient_instance, 'consultations': consultations})

#     return render(request, 'doctor/search_patient.html')

@login_required
def search_patient(request):
    if request.method == 'POST':
        
        doctor_user = request.user
        if doctor_user.user_type != '2':
          
            return redirect('search_patient')  

        
        patient_id = request.POST.get('patient_id')

        
        patient_instance = get_object_or_404(patient, patient_id=patient_id)

        
        appointments = Appointment.objects.filter(doctor=doctor_user, patient=patient_instance)
        if not appointments.exists():
           
            messages.warning(request, 'No appointments found for this patient with the current doctor.')
            return redirect('search_patient')  

       
        consultations = Consultation.objects.filter(appointment__in=appointments)

        return render(request, 'doctor/search_result.html', {'patient': patient_instance, 'consultations': consultations})

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
def r_search_patient(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient_instance = get_object_or_404(patient, patient_id=patient_id)
        
        
        appointments = Appointment.objects.filter(patient=patient_instance)
        
       
        consultations = Consultation.objects.filter(appointment__in=appointments)

        return render(request, 'reception/r_search_result.html', {'patient': patient_instance, 'consultations': consultations})

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
def p_search_patient(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient_instance = get_object_or_404(patient, patient_id=patient_id)
        
      
        appointments = Appointment.objects.filter(patient=patient_instance)
        
        
        consultations = Consultation.objects.filter(appointment__in=appointments)

        return render(request, 'pharmacy/p_search_result.html', {'patient': patient_instance, 'consultations': consultations})
    return render(request, 'pharmacy/p_search_patient.html')

@login_required
def pres_details(request):
   
    consultations = Consultation.objects.all()

    context = {
        'consultations': consultations,
    }

    return render(request, 'pharmacy/pres_details.html', context)

# def book_appointment(request):
#     departments = Department.objects.all()
#     doctors = CustomUser.objects.filter(user_type='2')

#     if request.method == 'POST':
#         patient_id = request.POST.get('patient_id')
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')
#         appointment_date = request.POST.get('appointment_date')

#         patient_instance = patient.objects.filter(patient_id=patient_id).first()

#         if patient_instance and department_id and doctor_id and appointment_date:
#             department_instance = Department.objects.get(pk=department_id)
#             doctor_instance = CustomUser.objects.get(pk=doctor_id)

#             # Generate a token based on your logic
#             token_number = str(random.randint(100000, 999999))

#             appointment = Appointment.objects.create(
#                 patient=patient_instance,
#                 department=department_instance,
#                 doctor=doctor_instance,
#                 token_number=token_number,
#                 appointment_date=appointment_date
#             )
#             appointment.save()

#             # Send an email to the patient
#             subject = 'Appointment Confirmation'
#             message = f'Your appointment is confirmed. Token Number: {token_number}'
#             from_email = settings.DEFAULT_FROM_EMAIL
#             to_email = [patient_instance.email]
#             send_mail(subject, message, from_email, to_email, fail_silently=True)

#             return redirect('appointment_details') 

#     return render(request, 'reception/book_appointment.html', {'departments': departments, 'doctors': doctors})
from django.urls import reverse



@login_required
def appointment_details(request, patient_id):
    
    appointments = Appointment.objects.filter(patient__patient_id=patient_id)

    context = {
        'appointments': appointments,
    }

    return render(request, 'reception/appointment_details.html', context)

# def reassign_patient(request):
#     current_doctor = request.user
#     appointments = Appointment.objects.filter(doctor=current_doctor)
#     all_doctors = CustomUser.objects.filter(user_type=2)

#     if request.method == 'POST':
#         patient_id = request.POST.get('patient')
#         new_doctor_id = request.POST.get('new_doctor')
#         reason = request.POST.get('reason')

#         patient_instance = patient.objects.get(id=patient_id)
#         new_doctor = CustomUser.objects.get(id=new_doctor_id)

#         PatientReassignment.objects.create(
#             patient=patient_instance,
#             current_doctor=current_doctor,
#             new_doctor=new_doctor,
#             reassignment_date=timezone.now(), 
#             reason=reason
#         )

#         
#         return redirect('reassign_patient')

#     return render(request, 'doctor/reassign_patient.html', {'appointments': appointments, 'all_doctors': all_doctors, 'current_doctor': current_doctor})

# def reassign_patient(request):
#     current_doctor = request.user
#     appointments = Appointment.objects.filter(doctor=current_doctor)
#     all_doctors = CustomUser.objects.filter(user_type=2)

#     if request.method == 'POST':
#         patient_id = request.POST.get('patient')
#         new_doctor_id = request.POST.get('new_doctor')
#         reason = request.POST.get('reason')
#         illness = request.POST.get('illness')
#         medicine_name = request.POST.get('medicine_name')
#         consumption_time = request.POST.get('consumption_time')

#         patient_instance = patient.objects.get(id=patient_id)
#         new_doctor = CustomUser.objects.get(id=new_doctor_id)

#        
#         PatientReassignment.objects.create(
#             patient=patient_instance,
#             current_doctor=current_doctor,
#             new_doctor=new_doctor,
#             illness=illness,
#             medicine_name=medicine_name,
#             consumption_time=consumption_time,
#             reassignment_date=timezone.now(),
#             reason=reason
#         )

#         
#         return redirect('reassign_patient')

#     return render(request, 'doctor/reassign_patient.html', {'appointments': appointments, 'all_doctors': all_doctors, 'current_doctor': current_doctor})


def reassign_patient_success(request):
    return render(request,'doctor/reassign_patient_success.html')

@login_required
def reassigned_details(request):
    current_doctor = request.user
    reassigned_patients = PatientReassignment.objects.filter(new_doctor=current_doctor)
    
    return render(request, 'doctor/reassigned_details.html', {'reassigned_patients': reassigned_patients})

@login_required
def recent_prescriptions(request):
    recent_prescriptions = Consultation.objects.all().order_by('-timestamp')[:3] 

    return render(request, 'pharmacy/recent_prescriptions.html', {'recent_prescriptions': recent_prescriptions})

# def book_appointment(request):
#     departments = Department.objects.all()
#     doctors = CustomUser.objects.filter(user_type='2')

#     if request.method == 'POST':
#         patient_id = request.POST.get('patient_id')
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')
#         appointment_date = request.POST.get('appointment_date')

#         patient_instance = patient.objects.filter(patient_id=patient_id).first()

#         if patient_instance and department_id and doctor_id and appointment_date:
#             department_instance = Department.objects.get(pk=department_id)
#             doctor_instance = CustomUser.objects.get(pk=doctor_id)

#             
#             token_number = str(random.randint(100000, 999999))

#             appointment = Appointment.objects.create(
#                 patient=patient_instance,
#                 department=department_instance,
#                 doctor=doctor_instance,
#                 token_number=token_number,
#                 appointment_date=appointment_date
#             )
#             appointment.save()

#             # Send an email to the patient
#             subject = 'Appointment Confirmation'
#             message = f'Your appointment is confirmed. Token Number: {token_number}'
#             from_email = settings.DEFAULT_FROM_EMAIL
#             to_email = [patient_instance.email]
#             send_mail(subject, message, from_email, to_email, fail_silently=True)

#             return render(request, 'reception/appointment_details.html', {'patient_id': patient_id, 'appointment_id': appointment.id})

#     return render(request, 'reception/book_appointment.html', {'departments': departments, 'doctors': doctors})

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q

# def book_appointment(request):
#     if request.method == 'POST':
#         patient_id = request.POST['patient_id']
#         department_id = request.POST['department']
#         doctor_id = request.POST['doctor']
#         appointment_time = request.POST['appointment_time']

#         
#         token_number = "ABC123"

#      
#         appointment = Appointment.objects.create(
#             patient=patient.objects.get(patient_id=patient_id),
#             department=Department.objects.get(pk=department_id),
#             doctor=CustomUser.objects.get(pk=doctor_id),
#             token_number=token_number,
#             appointment_time=appointment_time
#         )
#         appointment.save

#         
#         patient_email = patient.objects.get(patient_id=patient_id).email
#         subject = 'Appointment Confirmation'
#         message = f'Your appointment is confirmed. Token Number: {token_number}'
#         from_email = settings.DEFAULT_FROM_EMAIL
#         send_mail(subject, message, from_email, [patient_email])

#         return HttpResponse('Appointment booked successfully. Email sent to patient.')
#     else:
#         departments = Department.objects.all()
#         doctors = CustomUser.objects.filter(user_type='2')

#         # Filter doctors based on the selected department if a department is selected
#         selected_department = request.GET.get('department')
#         if selected_department:
#             doctors = doctors.filter(Q(userdetails__department__id=selected_department))

#         return render(request, 'reception/book_appointment.html', {'departments': departments, 'doctors': doctors})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        
        patient_id = request.POST['patient_id']
        department_id = request.POST['department']
        doctor_id = request.POST['doctor']
        appointment_date = request.POST['appointment_date']

       
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

        return render(request, 'reception/appointment_details.html', {'patient_id': patient_id, 'appointment': appointment})

    else: 
        departments = Department.objects.all()
        selected_department = request.GET.get('department')
        doctors = CustomUser.objects.filter(user_type='2')

        
        if selected_department:
            doctors = CustomUser.objects.filter(Q(userdetails__department__id=selected_department))

        return render(request, 'reception/book_appointment.html', {'departments': departments, 'doctors': doctors, 'selected_department': selected_department})