from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(AbstractUser):
    user_type=models.CharField(default=1,max_length=10)

class Department(models.Model):
    department_name=models.CharField(max_length=255,null=True)
    description=models.CharField(max_length=255,null=True)

class userdetails(models.Model):
    department=models.ForeignKey(Department,on_delete=models.CASCADE,null=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    number=models.CharField(max_length=255)
    image=models.ImageField(upload_to="image/",null=True)

class patient(models.Model):
    patient_name=models.CharField(max_length=255,null=True)
    patient_address=models.CharField(max_length=255,null=True)
    mobile_number=models.CharField(max_length=255)
    email=models.EmailField()
    patient_id = models.CharField(max_length=20,null=True, unique=True)

class Appointment(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token_number = models.CharField(max_length=10, unique=True)
    appointment_date = models.DateTimeField(null=True)

class Consultation(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    illness = models.TextField()
    consumption_time = models.CharField(max_length=20) 
    timestamp = models.DateTimeField(auto_now_add=True)
    
class PatientReassignment(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    current_doctor = models.ForeignKey(CustomUser, related_name='current_doctor_reassignments', on_delete=models.CASCADE)
    new_doctor = models.ForeignKey(CustomUser, related_name='new_doctor_reassignments', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null=True)
    illness = models.TextField(null=True)
    medicine_name = models.CharField(max_length=255, null=True)
    consumption_time = models.CharField(max_length=20, null=True)
    reassignment_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True)
