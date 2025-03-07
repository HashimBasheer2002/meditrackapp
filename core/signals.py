from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Hospital, Doctor

@receiver(m2m_changed, sender=Hospital.affiliated_hospitals.through)
def update_doctors_affiliation(sender, instance, action, **kwargs):
    if action == "post_add":  # Only trigger when hospitals become affiliated
        for hospital in instance.affiliated_hospitals.all():
            doctors = Doctor.objects.filter(hospital=hospital)
            for doctor in doctors:
                print(f"Doctor {doctor.user.get_full_name()} from {hospital.name} is now available for referrals")
