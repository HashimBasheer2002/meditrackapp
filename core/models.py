from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now


# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("hospital", "Hospital"),
        ("doctor", "Doctor"),
        ("patient", "Patient"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

# Hospital Model
class Hospital(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(default=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=255,default=True)
    affiliated_hospitals = models.ManyToManyField("self", blank=True, symmetrical=True)


    def __str__(self):
        return self.name

class Specialization(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique specializations

    def __str__(self):
        return self.name


# Doctor Model
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    profile_picture = models.ImageField(upload_to="doctor_profiles/", default="default_profile.jpg")

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"




# Patient Model
CustomUser = get_user_model()

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Use CustomUser
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()
    phone = models.CharField(max_length=15)
    medical_history = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # ✅ New Profile Picture Field

    def __str__(self):
        return self.user.username


from django.db import models
from django.conf import settings

from django.db import models

from django.db import models


class Appointment(models.Model):
    CONSULTATION_TYPE_CHOICES = [
        ("Online", "Online"),
        ("In-Person", "In-Person"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Checked-In", "Checked-In"),
        ("Chat Started", "Chat Started"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    message = models.TextField(blank=True, null=True)  # Optional message for extra details
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_TYPE_CHOICES, default="In-Person")
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)  # Default fee
    is_new_patient = models.BooleanField(default=True)  # Track if the patient is new to the hospital

    def __str__(self):
        return f"{self.patient.user.username} - {self.doctor.user.username} on {self.date} at {self.time} ({self.consultation_type})"

class ChatMessage(models.Model):
    appointment = models.ForeignKey("Appointment", on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    is_new_patient = models.BooleanField(default=True)
    details = models.TextField()  # Medical prescription details
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    advice = models.TextField(blank=True, null=True)# When hospital provides medicine



class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="medical_records")
    diagnosis = models.TextField()
    prescription = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.patient.user.username} - {self.created_at.date()}"


class Feedback(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)  # Link feedback to hospital
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.hospital.name} ({self.rating}⭐)"


class Ambulance(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="ambulances")
    vehicle_number = models.CharField(max_length=50, unique=True)
    driver_name = models.CharField(max_length=100)
    driver_contact = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vehicle_number} - {self.hospital.name}"



class AmbulanceBooking(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255,db_default=True)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("On the Way", "On the Way"), ("Completed", "Completed")],
        default="Pending",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.username} - {self.ambulance.vehicle_number} ({self.status})"


class AffiliationRequest(models.Model):
    from_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="sent_requests")
    to_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")],
        default="Pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)



class Referral(models.Model):
    from_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='sent_referrals')
    to_doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='received_referrals')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class ResourceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]

    from_hospital = models.ForeignKey(Hospital, related_name="sent_resource_requests", on_delete=models.CASCADE)
    to_hospital = models.ForeignKey(Hospital, related_name="received_resource_requests", on_delete=models.CASCADE)
    resource_name = models.CharField(max_length=255)  # Example: ICU beds, ventilators
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource_name} ({self.quantity}) from {self.from_hospital} to {self.to_hospital} - {self.status}"


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorMessage(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)  # Assuming Doctor model exists
    hospital = models.ForeignKey("Hospital", on_delete=models.CASCADE)  # Assuming Hospital model exists
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.doctor.user.username} to {self.hospital.name}"



from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    hospital = models.ForeignKey("Hospital", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.doctor.user.username} to {self.hospital.name}"



from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

User = get_user_model()

class DoctorHospitalChatRoom(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    hospital = models.ForeignKey("Hospital", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Correct way

    def __str__(self):
        return f"Chat: {self.doctor.user.username} & {self.hospital.name}"

class DoctorHospitalChatMessage(models.Model):
    chat = models.ForeignKey(DoctorHospitalChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # Can be a doctor or hospital staff
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"

from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Complaint(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="complaints")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)  # Admin can mark it as resolved

    def __str__(self):
        return f"Complaint from {self.patient.username} - {self.subject}"



