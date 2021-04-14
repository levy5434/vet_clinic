from django.urls import path

from . import views

app_name = "app"
urlpatterns = [
    path("", views.index, name="index"),
    path("animals/", views.animals, name="animals"),
    path("doctors/", views.doctors, name="doctors"),
    path(
        "add_client_appointment/<int:appointment_id>/",
        views.add_client_appointment,
        name="add_client_appointment",
    ),
    path(
        "add_client_appointment_f/<int:appointment_id>/client/<int:client_id>/",
        views.add_client_appointment_f,
        name="add_client_appointment_f",
    ),
    path("doctors/<int:doctor_id>", views.doctor, name="doctor"),
    path(
        "reschedule/<int:appointment_id>/doctor/<int:doctor_id>/week/<int:week>",
        views.reschedule,
        name="reschedule",
    ),
    path(
        "reschedule_confirm/<int:appointment_id>/<int:slot_id>/<time>",
        views.reschedule_confirm,
        name="reschedule_confirm",
    ),
    path(
        "appointments_to_reschedule",
        views.appointments_to_reschedule,
        name="appointments_to_reschedule",
    ),
    path(
        "manage_slots/<int:doctor_id>/week/<int:week>/",
        views.manage_slots,
        name="manage_slots",
    ),
    path("animals/<int:animal_id>/disease/", views.disease, name="disease"),
    path(
        "animals/disease/<int:disease_id>",
        views.check_disease,
        name="check_disease",
    ),
    path("my_schedule/<int:week>/", views.my_schedule, name="my_schedule"),
    path("slot/<int:slot_id>", views.slot, name="slot"),
    path("delete_slot/<int:slot_id>", views.delete_slot, name="delete_slot"),
    path("add_slot/<int:doctor_id>/", views.add_slot, name="add_slot"),
    path("my_appointments/", views.my_appointments, name="my_appointments"),
    path(
        "appointment/<int:appointment_id>/",
        views.appointment,
        name="appointment",
    ),
    path(
        "appointment/<int:appointment_id>/delete",
        views.delete_appointment,
        name="delete_appointment",
    ),
    path(
        "edit_appointment/<int:appointment_id>/",
        views.edit_appointment,
        name="edit_appointment",
    ),
    path("make_appointment/", views.make_appointment, name="make_appointment"),
    path(
        "make_appointment_d/<int:service_id>/",
        views.make_appointment_d,
        name="make_appointment_d",
    ),
    path(
        "make_appointment_s/<int:service_id>/<int:doctor_id>/week/<int:week>/",
        views.make_appointment_s,
        name="make_appointment_s",
    ),
    path(
        "make_appointment_f/<int:service_id>/<int:slot_id>/<time>",
        views.make_appointment_f,
        name="make_appointment_f",
    ),
    path(
        "appointment/<int:appointment_id>/",
        views.appointment,
        name="appointment",
    ),
    path("browse_clients/", views.browse_clients, name="browse_clients"),
    path("browse_clients/<int:client_id>/", views.client, name="client"),
    path(
        "browse_clients/<int:client_id>/add_pet/",
        views.add_pet,
        name="add_pet",
    ),
    path(
        "browse_clients/pet/delete_pet/<int:pet_id>/",
        views.pet_delete,
        name="pet_delete",
    ),
    path(
        "browse_clients/pet/<int:pet_id>/add_disease",
        views.add_disease,
        name="add_disease",
    ),
    path(
        "browse_clients/medicine/delete_medicine/<int:medicine_id>/",
        views.medicine_delete,
        name="medicine_delete",
    ),
    path(
        "browse_clients/disease/delete_disease/<int:disease_id>/",
        views.disease_delete,
        name="disease_delete",
    ),
    path(
        "browse_clients/disease/<int:disease_id>/add_medicine/",
        views.add_medicine,
        name="add_medicine",
    ),
    path(
        "browse_clients/disease/edit_medicine/<int:medicine_id>/",
        views.edit_medicine,
        name="edit_medicine",
    ),
    path(
        "browse_clients/disease/edit_disease/<int:disease_id>/",
        views.edit_disease,
        name="edit_disease",
    ),
]
