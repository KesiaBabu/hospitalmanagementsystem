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

class Medicine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    expiry_date = models.DateField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity < 10
    
class Bill(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bill #{self.id} - {self.patient.patient_name}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)  # unit price

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
