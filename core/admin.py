from django.contrib import admin
from .models import CustomUser,Specialization

admin.site.register(CustomUser)
admin.site.register(Specialization)
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "hospital", "date", "time", "status")
    list_filter = ("status", "hospital", "doctor")
    search_fields = ("patient__user__username", "doctor__user__username", "hospital__name")