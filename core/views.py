import razorpay
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .forms import PatientRegistrationForm, HospitalRegistrationForm, DoctorRegistrationForm, \
    LoginForm, PatientProfileUpdateForm, RescheduleAppointmentForm, FeedbackForm, AmbulanceForm, AmbulanceBookingForm, \
    AffiliationRequestForm, ReferralForm, DoctorProfileForm, ComplaintForm
from .models import CustomUser, Hospital, Doctor, Patient, ChatMessage, Prescription, MedicalRecord, Feedback, \
    Ambulance, AmbulanceBooking, AffiliationRequest, Referral, DoctorMessage, Message, Complaint
from django.shortcuts import render, get_object_or_404




def home(request):
    return render(request,'home.html')


# 🔹 Patient Registration
from django.shortcuts import render, redirect
from .forms import PatientRegistrationForm

def patient_register(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # This automatically creates a patient and links it to the user
            return redirect("login_page")
    else:
        form = PatientRegistrationForm()
    return render(request, "patient_register.html", {"form": form})

# 🔹 Admin Adding Hospital

@login_required
def hospital_register(request):
    if request.user.role != "admin":
        return redirect("dashboard")  # Prevent unauthorized access

    if request.method == "POST":
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # ✅ Save user and hospital
            return redirect("hospital_list")  # ✅ Redirect to hospital list after registration
    else:
        form = HospitalRegistrationForm()

    return render(request, "hospital_register.html", {"form": form})
@login_required
def doctor_register(request):
    if request.user.role != "hospital":
        return redirect("dashboard")  # ❌ Unauthorized access

    try:
        hospital = Hospital.objects.get(user=request.user)  # ✅ Get the logged-in hospital
    except Hospital.DoesNotExist:
        return redirect("dashboard")  # ❌ Redirect if hospital does not exist

    if request.method == "POST":
        form = DoctorRegistrationForm(request.POST, hospital=hospital)  # ✅ Pass hospital
        if form.is_valid():
            form.save()
            hospital = request.user.hospital  # Ensure this gets the correct hospital
            return redirect(reverse("doctor_list", args=[hospital.id])) # ✅ Redirect to the doctor list
    else:
        form = DoctorRegistrationForm(hospital=hospital)  # ✅ Pass hospital

    return render(request, "doctor_register.html", {"form": form})





@login_required
def doctor_profile(request):
    if request.user.role != "doctor":
        return redirect("dashboard")

    doctor = Doctor.objects.get(user=request.user)

    return render(request, "doctor_profile.html", {"doctor": doctor})

@login_required
def edit_doctor_profile(request):
    if request.user.role != "doctor":
        return redirect("dashboard")

    doctor = Doctor.objects.get(user=request.user)

    if request.method == "POST":
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect("doctor_profile")
    else:
        form = DoctorProfileForm(instance=doctor)

    return render(request, "edit_doctor_profile.html", {"form": form})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Doctor, Hospital

@login_required
def doctor_list(request, hospital_id):
    doctors = Doctor.objects.filter(hospital_id=hospital_id)  # Filter doctors by hospital
    hospital = get_object_or_404(Hospital, id=hospital_id)  # Get hospital details for rendering

    # Check user type
    is_patient = hasattr(request.user, 'patient')  # Assuming a OneToOneField relationship in the Patient model
    is_hospital = hasattr(request.user, 'hospital')  # Assuming a OneToOneField relationship in the Hospital model

    return render(request, 'doctors_list.html', {
        'doctors': doctors,
        'hospital_id': hospital_id,
        'hospital': hospital,
        'is_patient': is_patient,
        'is_hospital': is_hospital
    })


# 🔹 Single Login View for Everyone
def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)

                # 🔹 Fixing Admin Redirection
                if user.is_superuser or user.role == "admin":
                    return redirect("admin_dashboard")  # ✅ Ensure admin goes to admin dashboard
                elif user.role == "hospital":
                    return redirect("hospital_dashboard")
                elif user.role == "doctor":
                    return redirect("doctor_dashboard")
                else:
                    return redirect("patient_dashboard")

        return render(request, "login.html", {"form": form, "error": "Invalid credentials"})

    form = LoginForm()
    return render(request, "login.html", {"form": form})

# 🔹 Dashboard Redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hospital, Patient, Ambulance, Feedback, Appointment

@login_required
def admin_dashboard(request):
    # Get the hospital associated with the logged-in admin
    hospital = None
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        hospital = None  # Handle case where no hospital is linked to the admin

    # Fetch all relevant data
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()  # ✅ Fetch all doctors
    ambulances = Ambulance.objects.all()
    feedbacks = Feedback.objects.all()
    appointments = Appointment.objects.all()

    # Context to pass to the template
    context = {
        'hospital': hospital,
        'patients': patients,
        'doctors': doctors,  # ✅ Added doctors to context
        'ambulances': ambulances,
        'feedbacks': feedbacks,
        'appointments': appointments,
    }

    return render(request, "admin_dashboard.html", context)

@login_required
def hospital_dashboard(request):
    if request.user.role != "hospital":
        return redirect("dashboard")  # Prevent unauthorized access

    # Get the logged-in hospital instance
    hospital = get_object_or_404(Hospital, user=request.user)

    # Fetch all chat rooms where the hospital is involved
    chats = DoctorHospitalChatRoom.objects.filter(hospital=hospital)

    # Fetch all feedback for this hospital
    feedback_list = Feedback.objects.filter(hospital=hospital).order_by("-created_at")

    return render(
        request,
        "hospital_dashboard.html",
        {"feedback_list": feedback_list, "chats": chats},
    )


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorHospitalChatRoom, Appointment

@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor
    hospital = doctor.hospital  # Get assigned hospital

    # Fetch chat room for doctor and hospital
    chat_room = None
    if hospital:
        chat_room = DoctorHospitalChatRoom.objects.filter(doctor=doctor, hospital=hospital).first()
        appointments = Appointment.objects.filter(hospital=hospital, doctor=doctor)
    else:
        appointments = []

    return render(
        request,
        "doctor_dashboard.html",
        {
            "hospital": hospital,
            "appointments": appointments,
            "chat_room": chat_room,  # ✅ Pass chat_room to template
        },
    )


@login_required
def patient_dashboard(request):
    return render(request, "patient_dashboard.html")

@login_required
def dashboard(request):
    if request.user.role == "admin":
        return render(request, "admin_dashboard.html")
    elif request.user.role == "hospital":
        return render(request, "hospital_dashboard.html")
    elif request.user.role == "doctor":
        return render(request, "doctor_dashboard.html")
    return render(request, "patient_dashboard.html")



def hospital_list(request):
    hospitals = Hospital.objects.all()
    return render(request, 'hospital_list.html', {'hospitals': hospitals})




@login_required
def update_patient_profile(request):
    patient = request.user.patient  # Get the logged-in patient's profile
    if request.method == "POST":
        form = PatientProfileUpdateForm(request.POST, request.FILES, instance=patient)  # ✅ Handle image uploads
        if form.is_valid():
            form.save()
            return redirect("patient_dashboard")  # Redirect to dashboard after update
    else:
        form = PatientProfileUpdateForm(instance=patient)

    return render(request, "update_profile.html", {"form": form})


@login_required
def patient_profile(request):
    patient = get_object_or_404(Patient, user=request.user)
    return render(request, "profile.html", {"patient": patient})


from .models import Appointment
from .forms import AppointmentForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import Doctor, Hospital, Appointment
from .forms import AppointmentForm

import razorpay
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Appointment, Doctor, Hospital
from .forms import AppointmentForm

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def book_appointment(request, hospital_id, doctor_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_fee = doctor.appointment_fee  # Ensure this is a DecimalField
            order_amount = int(appointment_fee * 100)  # Convert to paisa

            # Create a Razorpay Order
            try:
                razorpay_order = razorpay_client.order.create({
                    "amount": order_amount,
                    "currency": "INR",
                    "payment_capture": "1"
                })
            except razorpay.errors.BadRequestError as e:
                return JsonResponse({"error": str(e)}, status=400)

            # Store order and appointment details in session
            request.session["razorpay_order_id"] = razorpay_order["id"]
            request.session["appointment_data"] = {
                "date": str(form.cleaned_data["date"]),
                "time": str(form.cleaned_data["time"]),
                "consultation_type": form.cleaned_data["consultation_type"],
                "message": form.cleaned_data["message"],
                "hospital_id": hospital_id,
                "doctor_id": doctor_id,
                "appointment_fee": float(appointment_fee),
            }

            return render(request, "payment.html", {
                "order_id": razorpay_order["id"],
                "amount": order_amount,
                "amount_display": appointment_fee,
                "hospital": hospital,
                "doctor": doctor,
                "razorpay_key": settings.RAZORPAY_KEY_ID
            })

    else:
        form = AppointmentForm()

    return render(request, 'book_appointment.html', {'form': form, 'hospital': hospital, 'doctor': doctor})

@csrf_exempt
def razorpay_webhook(request):
    return HttpResponse("OK", status=200)

from django.shortcuts import redirect

from django.shortcuts import redirect
from django.contrib import messages

def payment_success(request):
    razorpay_order_id = request.session.get("razorpay_order_id")
    appointment_data = request.session.get("appointment_data")

    if not razorpay_order_id or not appointment_data:
        messages.error(request, "Session expired or invalid order.")
        return redirect("home")  # Redirect to home if session expired

    # Save the appointment
    appointment = Appointment.objects.create(
        patient=request.user.patient,
        hospital_id=appointment_data["hospital_id"],
        doctor_id=appointment_data["doctor_id"],
        date=appointment_data["date"],
        time=appointment_data["time"],
        consultation_type=appointment_data["consultation_type"],
        message=appointment_data["message"],
        appointment_fee=appointment_data["appointment_fee"],
        status="Confirmed"
    )

    # Clear session data
    request.session.pop("razorpay_order_id", None)
    request.session.pop("appointment_data", None)

    messages.success(request, "Your appointment has been successfully booked.")

    # Redirect to "My Appointments"
    return redirect("patient_appointments")  # Ensure this URL is correct in `urls.py`



def appointment_success(request, appointment_id):
    # Retrieve the appointment object using the appointment_id from the URL
    appointment = Appointment.objects.get(id=appointment_id)

    # Get related doctor and hospital info if needed
    doctor = appointment.doctor
    hospital = appointment.hospital

    return render(request, 'appointment_success.html', {
        'appointment': appointment,
        'doctor': doctor,
        'hospital': hospital,
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def doctor_appointments(request):
    doctor = request.user.doctor  # Assuming the doctor is logged in
    appointments = Appointment.objects.filter(doctor=doctor).order_by("date", "time")
    return render(request, "appointments.html", {"appointments": appointments})



@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user == appointment.doctor.user:  # Ensure only the correct doctor can confirm
        appointment.status = "Confirmed"
        appointment.save()
    return redirect("doctor_appointments")

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user == appointment.doctor.user:
        appointment.status = "Cancelled"
        appointment.save()
    return redirect("doctor_appointments")


@login_required
def patient_appointments(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by("date", "time")
    return render(request, "my_appointments.html", {"appointments": appointments})





def hospital_appointments(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    appointments = Appointment.objects.filter(hospital=hospital).order_by("date", "time").distinct()

    return render(request, "hospital_appointments.html", {"hospital": hospital, "appointments": appointments})

from django.urls import reverse
def update_checkin(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.consultation_type == "In-Person" and appointment.status == "Confirmed":
        appointment.status = "Checked-In"
        appointment.save()

    return redirect(reverse("hospital_appointments", args=[appointment.hospital.id]))


@login_required
def confirm_online_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user == appointment.doctor.user and appointment.consultation_type == "Online":
        appointment.status = "Start Chat"  # Doctor sees "Start Chat"
        appointment.patient_status = "Confirmed"  # Patient sees only "Confirmed"
        appointment.save()

    return redirect("doctor_appointments")

@login_required
def start_chat(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user == appointment.doctor.user and appointment.status == "Confirmed":
        appointment.status = "Chat Started"
        appointment.save()

    return redirect("doctor_appointments")


from django.utils.timezone import now

@login_required
def chat(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure only the doctor and patient can access the chat
    if request.user != appointment.doctor.user and request.user != appointment.patient.user:
        return redirect("doctor_appointments")  # Redirect unauthorized users

    # Fetch chat messages
    messages = ChatMessage.objects.filter(appointment=appointment).order_by("timestamp")

    if request.method == "POST":
        message_content = request.POST.get("message")
        if message_content:
            ChatMessage.objects.create(
                appointment=appointment,
                sender=request.user,
                content=message_content,
                timestamp=now(),
            )
            # Ensure status is "Chat Started" if a message is sent
            if appointment.status != "Chat Started":
                appointment.status = "Chat Started"
                appointment.save()

        return redirect("chat", appointment_id=appointment_id)  # Refresh chat page

    return render(request, "chat.html", {"appointment": appointment, "messages": messages})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment, Prescription

@login_required
def end_consultation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user != appointment.doctor.user:
        return redirect("doctor_dashboard")

    if request.method == "POST":
        is_new_patient = request.POST.get("is_new_patient") == "yes"
        prescription_details = request.POST.get("prescription")
        diagnosis_details = request.POST.get("diagnosis")
        advice = request.POST.get("advice")  # Get doctor's advice from form

        if not diagnosis_details:
            messages.error(request, "Diagnosis is required.")
            return redirect("end_consultation", appointment_id=appointment.id)

        # Create or update Prescription
        prescription, created = Prescription.objects.get_or_create(
            appointment=appointment,
            defaults={
                "doctor": appointment.doctor,
                "patient": appointment.patient,
                "is_new_patient": is_new_patient,
                "details": prescription_details,
                "advice": advice,  # Save advice
            }
        )

        if not created:
            prescription.is_new_patient = is_new_patient
            prescription.details = prescription_details
            prescription.advice = advice
            prescription.save()

        # Create Medical Record
        MedicalRecord.objects.create(
            patient=appointment.patient,
            doctor=appointment.doctor,
            hospital=appointment.hospital,
            appointment=appointment,
            diagnosis=diagnosis_details,
            prescription=prescription_details,
        )

        # Update Appointment Status
        appointment.status = "Completed"
        appointment.save()

        return redirect("doctor_dashboard")

    return render(request, "prescription.html", {"appointment": appointment})




@login_required
def mark_prescription_done(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)

    if request.user.hospital != record.hospital:
        return redirect("hospital_dashboard")

    record.appointment.status = "Medicine Given"
    record.appointment.save()

    return redirect("hospital_dashboard")


@login_required
def hospital_prescriptions(request):
    if request.user.role != "hospital":
        return redirect("dashboard")  # Prevent unauthorized access

    hospital = request.user.hospital
    pending_prescriptions = MedicalRecord.objects.filter(hospital=hospital, appointment__status="Completed")

    return render(request, "hospital_prescriptions.html", {"prescriptions": pending_prescriptions})


@login_required
def mark_prescription_done(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)

    if request.user.role != "hospital":
        return redirect("hospital_prescriptions")

    record.appointment.status = "Medicine Given"
    record.appointment.save()

    return redirect("hospital_prescriptions")



@login_required
def patient_prescription_history(request):
    prescriptions = Prescription.objects.filter(patient=request.user.patient).order_by("-appointment__date")

    return render(request, "patient_prescriptions.html", {"prescriptions": prescriptions})


@login_required
def doctor_view_patient_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # Ensure the user is a doctor
    if not hasattr(request.user, "doctor"):
        return redirect("dashboard")

    doctor = request.user.doctor

    # Filter medical records only from the doctor's hospital
    medical_records = MedicalRecord.objects.filter(
        patient=patient, hospital=doctor.hospital
    ).order_by("-appointment__date")

    return render(request, "patient_history.html", {
        "patient": patient,
        "medical_records": medical_records
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if appointment.status in ["Completed", "Cancelled"]:
        messages.error(request, "You cannot cancel this appointment.")
        return redirect("patient_dashboard")

    appointment.status = "Cancelled"
    appointment.save()
    messages.success(request, "Your appointment has been successfully cancelled.")
    return redirect("patient_dashboard")

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if appointment.status != "Confirmed":
        messages.error(request, "Only confirmed appointments can be rescheduled.")
        return redirect("patient_dashboard")

    if request.method == "POST":
        form = RescheduleAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Your appointment has been rescheduled.")
            return redirect("patient_dashboard")
    else:
        form = RescheduleAppointmentForm(instance=appointment)

    return render(request, "reschedule_appointment.html", {"form": form, "appointment": appointment})



@login_required
def submit_feedback(request, appointment_id):
    patient = get_object_or_404(Patient, user=request.user)  # Get Patient instance
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = patient.user  # ✅ Assign the CustomUser instance
            feedback.hospital = appointment.hospital
            feedback.save()
            return redirect("patient_appointments")
    else:
        form = FeedbackForm()

    return render(request, "submit_feedback.html", {"form": form, "hospital": appointment.hospital})


@login_required
def hospital_feedback_list(request):
    # Ensure the logged-in user is a hospital
    hospital = get_object_or_404(Hospital, user=request.user)

    # Fetch feedback only for this hospital
    feedback_list = Feedback.objects.filter(hospital=hospital).order_by("-created_at")

    return render(request, "hospital_feedback_list.html", {"feedback_list": feedback_list})

@login_required
def add_ambulance(request):
    if request.user.role == "hospital":  # Ensure only hospitals can add ambulances
        if request.method == "POST":
            form = AmbulanceForm(request.POST)
            if form.is_valid():
                ambulance = form.save(commit=False)
                ambulance.hospital = request.user.hospital  # Assign hospital automatically
                ambulance.save()
                return redirect("hospital_dashboard")  # Redirect to hospital's dashboard
        else:
            form = AmbulanceForm()
        return render(request, "add_ambulance.html", {"form": form})

    return redirect("home")  # Redirect non-hospital users


@login_required
def book_ambulance(request):
    if request.method == "POST":
        form = AmbulanceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.patient = request.user  # Assign patient automatically
            booking.save()
            return JsonResponse({"message": "Ambulance booked successfully!"}, status=200)
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    hospitals = Hospital.objects.all()
    return render(request, "book_ambulance.html", {"hospitals": hospitals})


@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(AmbulanceBooking, id=booking_id)

    if request.user.role == "hospital":  # Ensure only hospital admins can update status
        if request.method == "POST":
            new_status = request.POST.get("status")
            if new_status in ["Pending", "Accepted", "On the Way", "Completed"]:
                booking.status = new_status
                booking.save()

    return redirect("hospital_ambulance_bookings", hospital_id=booking.ambulance.hospital.id)

@login_required
def track_ambulance(request):
    bookings = AmbulanceBooking.objects.filter(patient=request.user)
    return render(request, "track_ambulance.html", {"bookings": bookings})


def get_ambulances(request, hospital_id):
    ambulances = Ambulance.objects.filter(hospital_id=hospital_id, is_available=True)
    data = [{"id": amb.id, "vehicle_number": amb.vehicle_number} for amb in ambulances]
    return JsonResponse({"ambulances": data})

def view_ambulances(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    ambulances = Ambulance.objects.filter(hospital=hospital)
    return render(request, 'view_ambulances.html', {'ambulances': ambulances})


@login_required
def hospital_ambulance_bookings(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    bookings = AmbulanceBooking.objects.filter(ambulance__hospital=hospital)
    return render(request, 'hospital_ambulance_bookings.html', {'bookings': bookings})


from django.shortcuts import render
from django.http import HttpResponse
from .models import Prescription, MedicalRecord, Patient


@login_required
def doctor_prescription_history(request):
    if hasattr(request.user, 'doctor'):  # Ensure the user is a doctor
        # If search term is provided, filter records based on patient username
        search_query = request.GET.get('search', '')

        if search_query:
            # Fetch medical records of the patient across all doctors and hospitals
            patient = Patient.objects.filter(user__username__icontains=search_query).first()
            if patient:
                medical_records = MedicalRecord.objects.filter(patient=patient).order_by("-created_at")
            else:
                medical_records = []
        else:
            # Show prescriptions from the logged-in doctor
            prescriptions = Prescription.objects.filter(doctor=request.user.doctor).order_by("-appointment__date")

            # Fetch related medical records and diagnosis
            prescription_data = []
            for prescription in prescriptions:
                medical_record = MedicalRecord.objects.filter(appointment=prescription.appointment).first()
                diagnosis = medical_record.diagnosis if medical_record else "No Diagnosis Available"

                prescription_data.append({
                    "patient": prescription.patient,
                    "diagnosis": diagnosis,
                    "details": prescription.details,
                    "appointment_date": prescription.appointment.date,
                })

            return render(request, "doctor_prescriptions.html", {"prescriptions": prescription_data})

        # Return the results for the search query
        return render(request, "doctor_prescriptions.html", {
            "medical_records": medical_records,
            "search_query": search_query
        })

    return HttpResponse("Unauthorized", status=401)


def send_affiliation_request(request):
    if request.method == "POST":
        form = AffiliationRequestForm(request.POST)
        if form.is_valid():
            from_hospital = form.cleaned_data["from_hospital"]
            to_hospital = form.cleaned_data["to_hospital"]

            # Check if a request already exists
            if AffiliationRequest.objects.filter(from_hospital=from_hospital, to_hospital=to_hospital, status="Pending").exists():
                messages.error(request, "Affiliation request already sent.")
            else:
                form.save()
                messages.success(request, "Affiliation request sent successfully.")
            return redirect("hospital_dashboard")

    else:
        form = AffiliationRequestForm()

    return render(request, "send_affiliation_request.html", {"form": form})

# View to accept or reject an affiliation request
def manage_affiliation_request(request, request_id):
    affiliation_request = get_object_or_404(AffiliationRequest, id=request_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            affiliation_request.status = "Accepted"
            affiliation_request.save()

            # Add hospitals as affiliates
            affiliation_request.from_hospital.affiliated_hospitals.add(affiliation_request.to_hospital)
            affiliation_request.to_hospital.affiliated_hospitals.add(affiliation_request.from_hospital)

            messages.success(request, "Affiliation request accepted.")
        elif action == "reject":
            affiliation_request.status = "Rejected"
            affiliation_request.save()
            messages.warning(request, "Affiliation request rejected.")

        return redirect("hospital_dashboard")

    return render(request, "manage_affiliation_request.html", {"affiliation_request": affiliation_request})


def manage_affiliation_requests(request):
    requests = AffiliationRequest.objects.filter(to_hospital=request.user.hospital, status="Pending")
    return render(request, "manage_affiliation_requests.html", {"requests": requests})



def view_affiliated_hospitals(request):
    hospital = request.user.hospital  # Make sure the user has a hospital assigned!
    affiliated_hospitals = hospital.affiliated_hospitals.all()

    return render(request, "affiliated_hospitals.html", {"affiliated_hospitals": affiliated_hospitals})




def refer_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    hospital = request.user.doctor.hospital  # Get the logged-in doctor's hospital
    affiliated_hospitals = hospital.affiliated_hospitals.all()  # Get affiliated hospitals

    doctors = Doctor.objects.filter(hospital__in=affiliated_hospitals)  # Fetch doctors from affiliated hospitals

    if request.method == "POST":
        form = ReferralForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.patient = patient
            referral.referred_by = request.user.doctor
            referral.save()
            return redirect("some_success_page")  # Redirect after successful referral
    else:
        form = ReferralForm()

    return render(request, "send_referral.html", {"form": form, "patient": patient, "doctors": doctors})

def manage_referrals(request):
    doctor = request.user.doctor
    referrals = Referral.objects.filter(to_doctor=doctor, status="Pending")

    return render(request, "manage_referrals.html", {"referrals": referrals})

def update_referral_status(request, referral_id, action):
    referral = get_object_or_404(Referral, id=referral_id)

    if action == "accept":
        referral.status = "Accepted"
        messages.success(request, "Referral accepted.")
    elif action == "reject":
        referral.status = "Rejected"
        messages.warning(request, "Referral rejected.")

    referral.save()
    return redirect("manage_referrals")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def view_affiliated_hospitals(request):
    user = request.user

    # Ensure the user is associated with a hospital
    if hasattr(user, "hospital"):
        hospital = user.hospital
        affiliated_hospitals = hospital.affiliated_hospitals.all()
        return render(request, "affiliated_hospitals.html", {"affiliated_hospitals": affiliated_hospitals})

    # If user is not associated with a hospital, show an error page or redirect
    return render(request, "error.html", {"message": "You must be a hospital administrator to view affiliated hospitals."})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json
from .models import Hospital, ResourceRequest

def send_resource_request(request):
    affiliated_hospitals = request.user.hospital.affiliated_hospitals.all()
    if request.method == "POST":
        to_hospital_id = request.POST.get("to_hospital")
        resource_name = request.POST.get("resource_name")
        quantity = request.POST.get("quantity")
        to_hospital = get_object_or_404(Hospital, id=to_hospital_id)
        ResourceRequest.objects.create(from_hospital=request.user.hospital, to_hospital=to_hospital, resource_name=resource_name, quantity=quantity)
        return redirect("dashboard")

    return render(request, "send_resource_request.html", {"affiliated_hospitals": affiliated_hospitals})

# View received resource requests
def received_resource_requests(request):
    resource_requests = ResourceRequest.objects.filter(to_hospital=request.user.hospital)
    return render(request, "received_resource_requests.html", {"resource_requests": resource_requests})

# Approve resource request
def approve_resource_request(request, request_id):
    resource_request = get_object_or_404(ResourceRequest, id=request_id)
    resource_request.status = "approved"
    resource_request.save()
    return redirect("received_resource_requests")

# Deny resource request
def deny_resource_request(request, request_id):
    resource_request = get_object_or_404(ResourceRequest, id=request_id)
    resource_request.status = "denied"
    resource_request.save()
    return redirect("received_resource_requests")


@login_required
def view_resource_requests(request):
    """ View to check the status of resource requests (sent & received) """
    hospital = request.user.hospital
    sent_requests = ResourceRequest.objects.filter(from_hospital=hospital)
    received_requests = ResourceRequest.objects.filter(to_hospital=hospital)

    return render(request, 'received_resource_requests.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })



def about(request):
    return render(request, 'about.html')


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the login page after logout


@login_required
def hospital_all_prescriptions(request):
    # Ensure only hospitals can access
    if request.user.role != "hospital":
        return redirect("dashboard")

    # Get the logged-in hospital instance
    hospital = get_object_or_404(Hospital, user=request.user)

    # Fetch all prescriptions linked to this hospital through doctors
    prescriptions = Prescription.objects.filter(doctor__hospital=hospital).order_by("-created_at")

    return render(request, "hospital_view_prescriptions.html", {"prescriptions": prescriptions})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import DoctorHospitalChatRoom, DoctorHospitalChatMessage, Doctor, Hospital




@login_required
def chat_room(request, chat_id):
    """Display the chat room between a doctor and a hospital."""
    chat = get_object_or_404(DoctorHospitalChatRoom, id=chat_id)

    # Ensure only the doctor or hospital involved can view it
    if request.user == chat.doctor.user or request.user == chat.hospital.user:
        messages = chat.messages.all()
        return render(request, "chat_room.html", {"chat": chat, "messages": messages})

    # Unauthorized access
    return HttpResponseForbidden("You do not have permission to access this chat.")



@login_required
def send_message(request, chat_id):
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()

        if not message_text:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        try:
            chat = DoctorHospitalChatRoom.objects.get(id=chat_id)  # ✅ Use correct model
        except DoctorHospitalChatRoom.DoesNotExist:
            return JsonResponse({"error": "Chat not found"}, status=404)

        message = DoctorHospitalChatMessage.objects.create(
            chat=chat, sender=request.user, message=message_text
        )

        return JsonResponse({
            "sender": request.user.username,
            "message": message.message,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import DoctorHospitalChatRoom, DoctorHospitalChatMessage, Doctor, Hospital


@login_required
def start_hospital_chat(request):
    doctor = request.user.doctor

    # Ensure the doctor has a hospital assigned
    hospital = getattr(doctor, "hospital", None)
    if not hospital:
        messages.error(request, "You are not assigned to any hospital.")
        return redirect("doctor_dashboard")

    # Get or create the chat room
    chat_room, created = DoctorHospitalChatRoom.objects.get_or_create(
        doctor=doctor, hospital=hospital
    )

    # Redirect to the chat room
    return redirect("chat_room", chat_id=chat_room.id)


@login_required
def chat_list(request):
    """Show all chats for the current user (doctor or hospital)."""
    if hasattr(request.user, "doctor"):
        # Doctors see their own chat with their hospital
        chats = DoctorHospitalChatRoom.objects.filter(doctor=request.user.doctor)
    elif hasattr(request.user, "hospital"):
        # Hospitals see all chats with doctors
        chats = DoctorHospitalChatRoom.objects.filter(hospital=request.user.hospital)
    else:
        chats = []

    return render(request, "chat_list.html", {"chats": chats})


@login_required
def hospital_messages(request):
    """Display all chat rooms for the hospital."""
    if hasattr(request.user, 'hospital'):
        chat_rooms = DoctorHospitalChatRoom.objects.filter(hospital=request.user.hospital)
        return render(request, "hospital_messages.html", {"chat_rooms": chat_rooms})

    return HttpResponseForbidden("You do not have permission to view this page.")


@login_required
def doctor_chats(request):
    if request.user.role != "hospital":
        return redirect("dashboard")

    hospital = get_object_or_404(Hospital, user=request.user)
    chats = DoctorHospitalChatRoom.objects.filter(hospital=hospital)

    return render(request, "doctor_chats.html", {"chats": chats})


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required



@login_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Ensure only the hospital can delete the doctor
    if request.user != doctor.hospital.user:
        return redirect("some_error_page")  # Redirect to an error page or show a message

    doctor.delete()
    return redirect("doctor_list")



@login_required
def view_doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)  # Get doctor details using doctor_id
    return render(request, 'doctor_profile.html', {'doctor': doctor})



#admin

def admin_view_all_patients(request):
    patients = Patient.objects.all()  # Fetching all registered patients
    return render(request, 'admin_view_all_patients.html', {'patients': patients})


def admin_view_all_ambulances(request):
    ambulances = Ambulance.objects.all()  # Fetching all registered ambulances
    return render(request, 'admin_view_all_ambulances.html', {'ambulances': ambulances})

def admin_view_all_feedbacks(request):
    feedbacks = Feedback.objects.all()  # Fetching all feedbacks
    return render(request, 'admin_view_all_feedbacks.html', {'feedbacks': feedbacks})


def admin_view_all_appointments(request):
    appointments = Appointment.objects.all()  # Fetching all appointments
    return render(request, 'admin_view_all_appointments.html', {'appointments': appointments})


@login_required
def admin_view_all_doctors(request):
    doctors = Doctor.objects.all()  # Fetch all doctors
    return render(request, 'admin_view_all_doctors.html', {'doctors': doctors})  # Use 'doctors' (plural)


# Admin view to view patient details


def admin_view_patient_details(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')  # Get records, latest first

    return render(request, 'admin_view_patient_details.html', {
        'patient': patient,
        'medical_records': medical_records,
    })


@login_required
def submit_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.patient = request.user  # Link complaint to the logged-in user
            complaint.save()
            return redirect('patient_dashboard')  # Redirect to patient dashboard after submission
    else:
        form = ComplaintForm()

    return render(request, "submit_complaint.html", {"form": form})

@login_required
def admin_view_complaints(request):
    complaints = Complaint.objects.all().order_by("-created_at")  # Show latest complaints first
    return render(request, "admin_view_complaints.html", {"complaints": complaints})


@login_required
def mark_complaint_resolved(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint.is_resolved = True
    complaint.save()
    return redirect('admin_view_complaints')
