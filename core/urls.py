from django.urls import path
from .views import patient_register, hospital_register, doctor_register, login_page, home, admin_dashboard, dashboard, \
    hospital_dashboard, hospital_list, doctor_list, doctor_dashboard, update_patient_profile, patient_profile, \
    patient_dashboard, book_appointment, appointment_success, patient_appointments, doctor_appointments, \
    confirm_appointment, cancel_appointment, hospital_appointments, update_checkin, start_chat, chat, end_consultation, \
    hospital_prescriptions, mark_prescription_done, patient_prescription_history, doctor_view_patient_history, \
    reschedule_appointment, submit_feedback, hospital_feedback_list, add_ambulance, book_ambulance, \
    update_booking_status, track_ambulance, get_ambulances, view_ambulances, hospital_ambulance_bookings, \
    doctor_prescription_history, send_affiliation_request, manage_affiliation_request, manage_affiliation_requests, \
    view_affiliated_hospitals, manage_referrals, update_referral_status, refer_patient, send_resource_request, \
    received_resource_requests, approve_resource_request, \
    deny_resource_request, view_resource_requests, about, logout_view, hospital_all_prescriptions, chat_list, chat_room, \
    send_message, start_hospital_chat, hospital_messages, doctor_chats, payment_success, doctor_profile, \
    edit_doctor_profile, delete_doctor, view_doctor_profile, admin_view_all_patients, admin_view_all_ambulances, \
    admin_view_all_feedbacks, admin_view_all_appointments, admin_view_all_doctors, admin_view_patient_details, \
    submit_complaint, admin_view_complaints, mark_complaint_resolved

urlpatterns = [
    path('',home,name="home"),
    path("register/patient/", patient_register, name="patient_register"),
    path("hospital_register/", hospital_register, name="hospital_register"),
    path("hospital_dashboard/", hospital_dashboard, name="hospital_dashboard"),
    path("patient_dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor_dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("register/doctor/", doctor_register, name="doctor_register"),
    path("login/", login_page, name="login_page"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/", dashboard, name="dashboard"),
    path("hospitals/", hospital_list, name="hospital_list"),
    path('hospital/<int:hospital_id>/doctors/',doctor_list, name='doctor_list'),
    path("profile/update/", update_patient_profile, name="update_patient_profile"),
    path("profile/", patient_profile, name="patient_profile"),
    path("book-appointment/", book_appointment, name="book_appointment"),
    path("hospital/<int:hospital_id>/doctor/<int:doctor_id>/book/", book_appointment, name="book_appointment"),
    path('appointment-success/<int:appointment_id>/', appointment_success, name='appointment_success'),
    path("my-appointments/", patient_appointments, name="patient_appointments"),

    # Doctor views
    path("doctor/appointments/", doctor_appointments, name="doctor_appointments"),
    path("appointment/confirm/<int:appointment_id>/", confirm_appointment, name="confirm_appointment"),
    path("appointment/cancel/<int:appointment_id>/", cancel_appointment, name="cancel_appointment"),

    # Hospital views
    path("hospital/<int:hospital_id>/appointments/", hospital_appointments, name="hospital_appointments"),
    path("appointment/<int:appointment_id>/checkin/", update_checkin, name="update_checkin"),
    path('start_chat/<int:appointment_id>/', start_chat, name='start_chat'),
    path("chat/<int:appointment_id>/", chat, name="chat"),
    path('appointments/<int:appointment_id>/end-consultation/',end_consultation, name='end_consultation'),
    path('hospital/prescriptions/', hospital_prescriptions, name='hospital_prescriptions'),
    path('hospital/prescription/<int:record_id>/done/', mark_prescription_done, name='mark_prescription_done'),
    path("patient/prescriptions/", patient_prescription_history, name="patient_prescription_history"),
    path("doctor/patient-history/<int:patient_id>/",doctor_view_patient_history, name="doctor_view_patient_history"),


    path("appointments/<int:appointment_id>/reschedule/", reschedule_appointment, name="reschedule_appointment"),
    path("appointments/<int:appointment_id>/feedback/", submit_feedback, name="submit_feedback"),
    path("hospital/feedback/", hospital_feedback_list, name="hospital_feedback"),
    path("affiliated-hospitals/", view_affiliated_hospitals, name="view_affiliated_hospitals"),

    path("ambulance/add/", add_ambulance, name="add_ambulance"),
    path("ambulance/book/", book_ambulance, name="book_ambulance"),
    path("ambulance/update-status/<int:booking_id>/<str:status>/", update_booking_status, name="update_booking_status"),
    path("ambulance/track/", track_ambulance, name="track_ambulance"),
    path("api/get-ambulances/<int:hospital_id>/", get_ambulances, name="get_ambulances"),
    path('hospital/<int:hospital_id>/ambulances/',view_ambulances, name='view_ambulances'),
    path("hospital/<int:hospital_id>/ambulance_bookings/", hospital_ambulance_bookings,name="hospital_ambulance_bookings"),
    path("ambulance/booking/<int:booking_id>/update/", update_booking_status, name="update_booking_status"),
    path("doctor/prescriptions/", doctor_prescription_history, name="doctor_prescription_history"),

    path("send-affiliation-request/", send_affiliation_request, name="send_affiliation_request"),
    path("manage-affiliation-requests/", manage_affiliation_requests, name="manage_affiliation_requests"),
    path("manage-affiliation-request/<int:request_id>/", manage_affiliation_request, name="manage_affiliation_request"),
    path("affiliated-hospitals/", view_affiliated_hospitals, name="view_affiliated_hospitals"),
    path('logout/', logout_view, name='logout'),



    path("manage-referrals/", manage_referrals, name="manage_referrals"),
    path("update-referral/<int:referral_id>/<str:action>/", update_referral_status, name="update_referral_status"),
    path("refer-patient/<int:patient_id>/", refer_patient, name="refer_patient"),



    path("send-resource/", send_resource_request, name="send_resource_request"),
    path("received-resource-requests/", received_resource_requests, name="received_resource_requests"),
    path("approve-resource-request/<int:request_id>/", approve_resource_request, name="approve_resource_request"),
    path("deny-resource-request/<int:request_id>/", deny_resource_request, name="deny_resource_request"),
    path('resource-requests/', view_resource_requests, name='view_resource_requests'),



    path('about/',about,name='about'),
    path("hospital-prescriptions/", hospital_all_prescriptions, name="hospital_all_prescriptions"),
    path("chat/start/", start_hospital_chat, name="start_hospital_chat"),
    path("hospital/chat/<int:chat_id>/", chat_room, name="chat_room"),
    path("chats/", chat_list, name="chat_list"),
    path("hospital/chat/<int:chat_id>/send/", send_message, name="send_message"),
    path("hospital/messages/", hospital_messages, name="hospital_messages"),
    path("hospital/chats/", doctor_chats, name="doctor_chats"),
    path("payment-success/", payment_success, name="payment_success"),
    path("doctor/profile/", doctor_profile, name="doctor_profile"),
    path("doctor/profile/edit/", edit_doctor_profile, name="edit_doctor_profile"),
    path("doctor/profile/<int:doctor_id>/", doctor_profile, name="doctor_profile"),
    path("doctor/delete/<int:doctor_id>/", delete_doctor, name="delete_doctor"),
    path('dr/profile/<int:doctor_id>/', view_doctor_profile, name='view_dr_profile'),



    path('all/patients/', admin_view_all_patients, name='admin_view_all_patients'),
    path('all/ambulances/', admin_view_all_ambulances, name='admin_view_all_ambulances'),
    path('all/feedbacks/', admin_view_all_feedbacks, name='admin_view_all_feedbacks'),
    path('all/appointments/', admin_view_all_appointments, name='admin_view_all_appointments'),
    path('all/doctors/', admin_view_all_doctors, name='admin_view_all_doctors'),
    path('patients/details/<int:patient_id>/', admin_view_patient_details, name='admin_view_patient_details'),

    path('submit-complaint/', submit_complaint, name='submit_complaint'),
    path('view/complaints/', admin_view_complaints, name='admin_view_complaints'),
    path('view/complaints/resolve/<int:complaint_id>/', mark_complaint_resolved, name='mark_complaint_resolved'),

]











