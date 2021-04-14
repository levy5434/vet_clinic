from datetime import date, datetime, time, timedelta

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from user.models import Doctor, Profile, Service, Slot

from .decorators import allowed_users, unauthenticated_user
from .forms import (AnimalForm, AppointmentForm, DayForm, DiseaseForm,
                    MedicineForm, SlotForm)
from .functions import (free_hours, next_weekday, scheduler, time_plus,
                        what_week, whole_week)
from .models import Animal, Appointment, Disease, Medicine


def index(request):
    if request.user.groups.filter(name__in=["Admin"]).exists():
        appointments = Appointment.objects.filter(slot__isnull=True).exists()
        if appointments:
            no_slot_appointments = True
            context = {"no_slot_appointments": no_slot_appointments}
            return render(request, "app/index.html", context)
    return render(request, "app/index.html")


def doctor(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    first, last = what_week(0)
    slots = Slot.objects.filter(
        doctor=doctor, date__range=[first, last]
    ).order_by("date")
    services = Service.objects.filter(doctor=doctor, admin_only=False)
    context = {"doctor": doctor, "slots": slots, "services": services}
    return render(request, "app/doctor.html", context)


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(client=request.user).order_by(
        "date"
    )
    upcoming_appointment = []
    today = date.today()
    past_appointments = []
    for appointment in appointments:
        if appointment.date >= today:
            upcoming_appointment = appointment
            appointments = appointments.exclude(id=upcoming_appointment.id)
            break
        else:
            past_appointments.append(appointment)
            appointments = appointments.exclude(id=appointment.id)
    context = {
        "appointments": appointments,
        "past_appointments": past_appointments,
        "upcoming_appointment": upcoming_appointment,
    }
    return render(request, "app/my_appointments.html", context)


@login_required
def make_appointment(request):
    if request.user.groups.filter(name__in=["Admin"]).exists():
        services = Service.objects.all()
    else:
        services = Service.objects.filter(admin_only=False)
    context = {"services": services}
    return render(request, "app/make_appointment.html", context)


@login_required
def appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    reschedule = True
    if appointment.slot:
        reschedule = False
    client = appointment.client
    delete = False
    if (
        appointment.date > date.today()
        and request.user == client
        or request.user.groups.filter(name__in=["Admin"]).exists()
    ):
        delete = True
    if request.user != client and not request.user.is_staff:
        raise PermissionDenied
    if appointment.animal:
        animal = appointment.animal
        appointments = Appointment.objects.filter(animal=animal).exclude(
            id=appointment_id
        )
        diseases = animal.disease_set.all()
        actual_diseases = []
        past_diseases = []
        for disease in diseases:
            if disease.status == False:
                past_diseases.append(disease)
            else:
                actual_diseases.append(disease)
        context = {
            "animal": animal,
            "actual_diseases": actual_diseases,
            "client": client,
            "past_diseases": past_diseases,
            "appointments": appointments,
            "appointment": appointment,
            "delete": delete,
            "reschedule": reschedule,
        }
    else:
        context = {
            "client": client,
            "appointment": appointment,
            "delete": delete,
            "reschedule": reschedule,
        }
    return render(request, "app/appointment.html", context)


@login_required
def make_appointment_d(request, service_id):
    if request.user.groups.filter(name__in=["Admin"]).exists():
        services = Service.objects.all().exclude(id=service_id)
        my_service = Service.objects.get(id=service_id)
    else:
        services = Service.objects.filter(admin_only=False).exclude(
            id=service_id
        )
        my_service = Service.objects.get(id=service_id)
        if my_service.admin_only == True:
            messages.success(request, _("This service is not available!"))
            return redirect("app:make_appointment")
    doctors = Doctor.objects.filter(services__id=service_id)
    context = {
        "services": services,
        "my_service": my_service,
        "doctors": doctors,
    }
    return render(request, "app/make_appointment_d.html", context)


@login_required
def make_appointment_s(request, service_id, doctor_id, week):
    if request.user.groups.filter(name__in=["Admin"]).exists():
        services = Service.objects.all().exclude(id=service_id)
        my_service = Service.objects.get(id=service_id)
    else:
        my_service = Service.objects.get(id=service_id)
        if my_service.admin_only == True:
            messages.success(request, _("This service is not available!"))
            return redirect("app:make_appointment")
        services = Service.objects.filter(admin_only=False).exclude(
            id=service_id
        )
    selected_doctor = Doctor.objects.get(id=doctor_id)
    more_hours = False
    n_week = week + 1
    p_week = week - 1
    first = what_week(week)[0]
    last = what_week(week)[1]
    all_slots = Slot.objects.filter(
        doctor=selected_doctor, date__range=[first, last]
    ).order_by("date")
    for slot in all_slots:
        if len(free_hours(slot.id, service_id)) > 5:
            more_hours = True
            break
    all_days = whole_week(week)
    days = []
    for day in all_days:
        days.append(day)
        for slot in all_slots:
            if slot.date == day:
                days.pop()
                days.append([day, slot])
    doctors = Doctor.objects.filter(services__id=service_id).exclude(
        id=doctor_id
    )
    context = {
        "services": services,
        "my_service": my_service,
        "doctors": doctors,
        "selected_doctor": selected_doctor,
        "days": days,
        "more_hours": more_hours,
        "week": week,
        "n_week": n_week,
        "p_week": p_week,
        "first": first,
        "last": last,
    }
    return render(request, "app/make_appointment_s.html", context)


@login_required
def make_appointment_f(request, service_id, slot_id, time):
    service = Service.objects.get(id=service_id)
    if (
        service.admin_only == True
        and not request.user.groups.filter(name__in=["Admin"]).exists()
    ):
        messages.success(request, _("This service is not available!"))
        return redirect("app:make_appointment")
    slot = Slot.objects.get(id=slot_id)
    times = free_hours(slot.id, service.id)
    doctor = slot.doctor
    if not doctor.services.filter(id=service.id).exists():
        messages.success(request, "This service is not available!")
        return redirect(
            "app:make_appointment_s",
            service_id=service.id,
            doctor_id=doctor.id,
            week=0,
        )
    available = False
    for f_time in times:
        if time == f_time.strftime("%H:%M:%S"):
            available = True
    if available == False:
        messages.success(request, "This hour is not available!")
        return redirect(
            "app:make_appointment_s",
            service_id=service.id,
            doctor_id=doctor.id,
            week=0,
        )
    user = User.objects.get(username=request.user.username)
    user_have_animal = Animal.objects.filter(owner=request.user)
    if request.method != "POST":
        if user_have_animal and not user.is_staff:
            form = AppointmentForm(initial={"animal": user_have_animal[0]})
        else:
            form = AppointmentForm()
        form.fields["animal"] = forms.ModelChoiceField(
            Animal.objects.filter(owner=request.user),
            required=False,
            empty_label="New Pet",
        )
    else:
        form = AppointmentForm(request.POST)
        if form.is_valid():
            if service.admin_only == True:
                appointment = Appointment(
                    service=service,
                    slot=slot,
                    doctor=doctor,
                    date=slot.date,
                    start_time=time,
                    information=request.POST["information"],
                )
                appointment.save()
                messages.success(
                    request, _("Success! Free time has been booked.")
                )
                return redirect("app:slot", slot_id=slot.id)
            elif request.user.groups.filter(name__in=["Admin"]).exists():
                text = f"""Owner: {request.POST['client_first_name']} {request.POST['client_last_name']}
                Phone Number: {request.POST['client_phone']}\n
                Pet:\nName: {request.POST['name']}\n Species: {request.POST['species']}\n Information:"""
                text = text + request.POST["information"]
                appointment = Appointment(
                    service=service,
                    slot=slot,
                    doctor=doctor,
                    date=slot.date,
                    start_time=time,
                    information=text,
                )
                appointment.save()
                messages.success(
                    request, _("Success! Appointment has been booked.")
                )
                return redirect("app:slot", slot_id=slot.id)
            elif request.POST["animal"]:
                animal = Animal.objects.get(id=request.POST["animal"])
                appointment = Appointment(
                    client=user,
                    animal=animal,
                    service=service,
                    doctor=doctor,
                    slot=slot,
                    date=slot.date,
                    start_time=time,
                    information=request.POST["information"],
                )
                messages.success(
                    request, _("Success! Appointment has been booked.")
                )
                return redirect("app:my_appointments")
            else:
                text = f"Name: {request.POST['name']}\n Species: {request.POST['species']}\n "
                text = text + request.POST["information"]
                appointment = Appointment(
                    client=user,
                    service=service,
                    slot=slot,
                    doctor=doctor,
                    date=slot.date,
                    start_time=time,
                    information=text,
                )
                appointment.save()
                messages.success(
                    request, _("Success! Appointment has been booked.")
                )
                return redirect("app:my_appointments")
    context = {
        "form": form,
        "service": service,
        "slot": slot,
        "doctor": doctor,
        "time": time,
        "user_have_animal": user_have_animal,
    }
    return render(request, "app/make_appointment_f.html", context)


@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.date < date.today():
        messages.success(
            request, _("You can not delete previous appointments")
        )
        return redirect("app:appointement", appointment_id=appointment_id)
    user = appointment.client
    if request.user == user:
        appointment.delete()
        messages.success(request, _("Appointment has been deleted"))
        return redirect("app:my_appointments")
    elif request.user.groups.filter(name__in=["Admin"]).exists():
        slot = Slot.objects.get(id=appointment.slot.id)
        appointment.delete()
        messages.success(request, _("Appointment has been deleted"))
        return redirect("app:slot", slot_id=slot.id)
    return redirect("app:index")


def doctors(request):
    doctors = Doctor.objects.all()
    context = {"doctors": doctors}
    return render(request, "app/doctors.html", context)


@login_required
def animals(request):
    animals = Animal.objects.filter(owner=request.user).order_by(
        "register_date"
    )
    if animals.count() == 1:
        return redirect("app:disease", animal_id=animals[0].id)
    context = {"animals": animals}
    return render(request, "app/animals.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def my_schedule(request, week):
    profile = Profile.objects.get(user=request.user.id)
    doctor = Doctor.objects.get(profile=profile)
    first, last = what_week(0)
    slots = Slot.objects.filter(
        doctor=doctor, date__range=[first, last]
    ).order_by("date")
    n_week = week + 1
    p_week = week - 1
    today = []
    first = what_week(week)[0]
    last = what_week(week)[1]
    for slot in slots:
        if slot.date == date.today():
            today = slot
    if today:

        context = {
            "slots": slots,
            "today": today,
            "week": week,
            "n_week": n_week,
            "p_week": p_week,
            "first": first,
            "last": last,
        }
    else:
        today_free = date.today()
        context = {
            "slots": slots,
            "today_free": today_free,
            "week": week,
            "n_week": n_week,
            "p_week": p_week,
            "first": first,
            "last": last,
        }
    return render(request, "app/my_schedule.html", context)


@login_required
def disease(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    client = animal.owner
    appointments = Appointment.objects.filter(animal=animal)
    if request.user != client and not request.user.is_staff:
        raise PermissionDenied
    diseases = animal.disease_set.all()
    actual_diseases = []
    past_diseases = []
    for disease in diseases:
        if disease.status == False:
            past_diseases.append(disease)
        else:
            actual_diseases.append(disease)
    context = {
        "animal": animal,
        "actual_diseases": actual_diseases,
        "client": client,
        "past_diseases": past_diseases,
        "appointments": appointments,
    }
    return render(request, "app/disease.html", context)


@login_required
def check_disease(request, disease_id):
    disease = Disease.objects.get(id=disease_id)
    medicines = disease.medicine_set.all()
    animal = disease.animal
    client = animal.owner
    if request.user != client and not request.user.is_staff:
        raise PermissionDenied
    context = {"disease": disease, "medicines": medicines, "animal": animal}
    return render(request, "app/check_disease.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def add_pet(request, client_id):
    client = User.objects.get(id=client_id)
    if request.method != "POST":
        form = AnimalForm()
    else:
        form = AnimalForm(data=request.POST)
        if form.is_valid():
            new_pet = form.save(commit=False)
            new_pet.owner = client
            new_pet.save()
            return redirect("app:client", client_id=client_id)
    context = {"form": form, "client": client}
    return render(request, "app/add_pet.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def browse_clients(request):
    clients = User.objects.all()
    query = request.GET.get("q")
    if query:
        clients = clients.filter(last_name__icontains=query)
    context = {"clients": clients}
    return render(request, "app/browse_clients.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def add_client_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if appointment.client:
        messages.success(request, _("Appointment has a client!"))
        return redirect("app:appointment", appointment_id=appointment.id)
    clients = User.objects.all()
    query = request.GET.get("q")
    if query:
        clients = clients.filter(last_name__icontains=query)
    context = {"clients": clients, "appointment": appointment}
    return render(request, "app/add_client_appointment.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def add_client_appointment_f(request, appointment_id, client_id):
    appointment = Appointment.objects.get(id=appointment_id)
    client = User.objects.get(id=client_id)
    if request.method == "POST":
        appointment.client = client
        appointment.save()
        messages.success(
            request, _("Client has been added to the appointment")
        )
        return redirect("app:appointment", appointment_id=appointment_id)
    context = {"appointment": appointment, "client": client}
    return render(request, "app/add_client_appointment_f.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def client(request, client_id):
    client = User.objects.get(id=client_id)
    appointments = Appointment.objects.filter(client=client).order_by(
        "date", "start_time"
    )
    past_appointments = []
    today = date.today()
    for appointment in appointments:
        if appointment.date < today:
            past_appointments.append(appointment)
            appointments = appointments.exclude(id=appointment.id)
        else:
            break
    animals = client.animal_set.all()
    context = {
        "client": client,
        "animals": animals,
        "appointments": appointments,
        "past_appointments": past_appointments,
    }
    return render(request, "app/client.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def appointments_to_reschedule(request):
    appointments = Appointment.objects.filter(slot__isnull=True)
    context = {"appointments": appointments}
    return render(request, "app/appointments_to_reschedule.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def add_disease(request, pet_id):
    pet = Animal.objects.get(id=pet_id)
    if request.method != "POST":
        form = DiseaseForm()
    else:
        form = DiseaseForm(data=request.POST)
        if form.is_valid():
            new_disease = form.save(commit=False)
            new_disease.animal = pet
            new_disease.doctor = (
                f"Added by: {request.user.first_name} {request.user.last_name}"
            )
            new_disease.save()
            messages.success(request, _("Disease has been added"))
            return redirect("app:disease", disease_id=new_disease.id)
    context = {"form": form, "pet": pet}
    return render(request, "app/add_disease.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def pet_delete(request, pet_id):
    pet = get_object_or_404(Animal, id=pet_id)
    client = pet.owner
    if request.method == "POST":
        pet.delete()
        messages.success(request, _("Pet has been deleted"))
        return redirect("app:client", client_id=client.id)
    context = {"client": client, "pet": pet}
    return render(request, "app/delete_pet.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def manage_slots(request, doctor_id, week):
    doctor = Doctor.objects.get(id=doctor_id)
    first, last = what_week(week)
    slots = Slot.objects.filter(
        doctor=doctor, date__range=[first, last]
    ).order_by("date")
    n_week = week + 1
    p_week = week - 1
    first = what_week(week)[0]
    last = what_week(week)[1]
    context = {
        "doctor": doctor,
        "slots": slots,
        "week": week,
        "n_week": n_week,
        "p_week": p_week,
        "first": first,
        "last": last,
    }
    return render(request, "app/manage_slots.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def delete_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    doctor = slot.doctor
    if request.method == "POST":
        slot.delete()
        messages.success(request, _("Slot have been deleted"))
        return redirect("app:manage_slots", doctor_id=doctor.id, week=0)
    context = {"slot": slot, "doctor": doctor}
    return render(request, "app/delete_slot.html", context)


@staff_member_required(login_url="app:index")
def slot(request, slot_id):
    slot = Slot.objects.get(id=slot_id)
    doctor = slot.doctor
    profile = doctor.profile
    user = profile.user
    if (
        request.user != user
        and not request.user.groups.filter(name__in=["Admin"]).exists()
    ):
        raise PermissionDenied
    appointments = Appointment.objects.filter(slot=slot).order_by("start_time")
    times, times1 = scheduler(slot.id)
    upcoming_appointment = []
    if date.today() == slot.date:
        now = datetime.now().time()
    else:
        now = time(5, 0, 0)
    for appointment in appointments:
        if now <= time_plus(
            appointment.start_time, appointment.service.duration
        ):
            upcoming_appointment = appointment
            appointments = appointments.exclude(id=upcoming_appointment.id)
            break
    times.sort(reverse=True)
    context = {
        "slot": slot,
        "appointments": appointments,
        "upcoming_appointment": upcoming_appointment,
        "times2": times,
        "times1": times1,
    }
    return render(request, "app/slot.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def add_medicine(request, disease_id):
    disease = Disease.objects.get(id=disease_id)
    animal = disease.animal
    if request.method != "POST":
        form = MedicineForm()
    else:
        form = MedicineForm(data=request.POST)
        if form.is_valid():
            new_medicine = form.save(commit=False)
            new_medicine.disease = disease
            new_medicine.doctor = (
                f"Added by: {request.user.first_name} {request.user.last_name}"
            )
            new_medicine.save()
            messages.success(request, _("Medicine has been added"))
            return redirect("app:check_disease", disease_id=disease.id)
    context = {"form": form, "disease": disease, "animal": animal}
    return render(request, "app/add_medicine.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def add_slot(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    first, last = what_week(0)
    slots = Slot.objects.filter(
        doctor=doctor, date__range=[first, last]
    ).order_by("date")
    if request.method != "POST":
        day_form = DayForm()
        slot_form = SlotForm()
    else:
        slot_form = SlotForm(request.POST)
        day_form = DayForm(request.POST)
        if slot_form.is_valid() and day_form.is_valid():
            day = day_form.cleaned_data.get("day")
            start_date = day_form.cleaned_data.get("start_date")
            end_date = day_form.cleaned_data.get("end_date")
            dates = next_weekday(day, start_date, end_date)
            if start_date < date.today() or end_date < start_date:
                messages.success(request, _("Wrong dates!"))
                return redirect("app:add_slot", doctor_id=doctor_id)
            for d_date in dates:
                ifslot = Slot.objects.filter(doctor=doctor, date=d_date)
                if ifslot:
                    messages.success(
                        request,
                        _("You can not add slot in this day of the week!"),
                    )
                    return redirect("app:add_slot", doctor_id=doctor_id)
            for d_date in dates:
                slot = Slot(
                    doctor=doctor,
                    date=d_date,
                    start_time=request.POST["start_time"],
                    end_time=request.POST["end_time"],
                )
                slot.save()
            messages.success(request, _("Slots have been added"))
            return redirect("app:doctor", doctor_id=doctor.id)
    context = {
        "slot_form": slot_form,
        "day_form": day_form,
        "doctor": doctor,
        "slots": slots,
    }
    return render(request, "app/add_slot.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def edit_medicine(request, medicine_id):
    medicine = Medicine.objects.get(id=medicine_id)
    disease = medicine.disease
    if request.method != "POST":
        form = MedicineForm(instance=medicine)
    else:
        form = MedicineForm(instance=medicine, data=request.POST)
        if form.is_valid():
            medicine.doctor = f"Edited by: {request.user.first_name} {request.user.last_name}"
            form.save()
            messages.success(request, _("Medicine has been updated"))
            return redirect("app:check_disease", disease_id=disease.id)
    context = {"disease": disease, "medicine": medicine, "form": form}
    return render(request, "app/edit_medicine.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def medicine_delete(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    disease = medicine.disease
    medicine.delete()
    messages.success(request, _("Medicine has been deleted"))
    return redirect("app:check_disease", disease_id=disease.id)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def disease_delete(request, disease_id):
    disease = get_object_or_404(Disease, id=disease_id)
    pet = disease.animal
    disease.delete()
    messages.success(request, _("Disease has been deleted"))
    return redirect("app:disease", animal_id=pet.id)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def reschedule(request, appointment_id, week, doctor_id):
    appointment = Appointment.objects.get(id=appointment_id)
    doctor = Doctor.objects.get(id=doctor_id)
    service = appointment.service
    client = appointment.client
    all_slots = Slot.objects.filter(doctor=doctor).order_by("date")
    slots = weekdays(all_slots, week)
    n_week = week + 1
    p_week = week - 1
    first = what_week(week)[0]
    last = what_week(week)[1]
    doctors = Doctor.objects.filter(services__id=service.id).exclude(
        id=doctor_id
    )
    context = {
        "appointment": appointment,
        "service": service,
        "doctor": doctor,
        "slots": slots,
        "client": client,
        "week": week,
        "n_week": n_week,
        "p_week": p_week,
        "first": first,
        "last": last,
        "doctors": doctors,
    }
    return render(request, "app/reschedule.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Admin"])
def reschedule_confirm(request, appointment_id, slot_id, time):
    appointment = Appointment.objects.get(id=appointment_id)
    client = appointment.client
    service = appointment.service
    slot = Slot.objects.get(id=slot_id)
    doctor = slot.doctor
    times = free_hours(slot.id, service.id)
    doctor = slot.doctor
    if not doctor.services.filter(id=service.id).exists():
        messages.success(request, _("This service is not available!"))
        return redirect(
            "app:reschedule",
            service_id=service.id,
            doctor_id=appointment.doctor.id,
            week=0,
        )
    available = False
    for f_time in times:
        if time == f_time.strftime("%H:%M:%S"):
            available = True
            break
    if available == False:
        messages.success(request, _("This hour is not available!"))
        return redirect(
            "app:reschedule",
            service_id=service.id,
            doctor_id=appointment.doctor.id,
            week=0,
        )
    if request.method == "POST":
        appointment.start_time = time
        appointment.slot = slot
        appointment.date = slot.date
        appointment.doctor = doctor
        appointment.save()
        messages.success(request, _("Appointment has been rescheduled"))
        return redirect("app:appointment", appointment_id=appointment.id)
    context = {
        "appointment": appointment,
        "slot": slot,
        "doctor": doctor,
        "client": client,
        "time": time,
    }
    return render(request, "app/reschedule_confirm.html", context)


@staff_member_required(login_url="app:index")
@allowed_users(allowed_roles=["Doctors"])
def edit_disease(request, disease_id):
    disease = Disease.objects.get(id=disease_id)
    animal = disease.animal
    if request.method != "POST":
        form = DiseaseForm(instance=disease)
    else:
        form = DiseaseForm(instance=disease, data=request.POST)
        if form.is_valid():
            disease.doctor = f"Edited by: {request.user.first_name} {request.user.last_name}"
            form.save()
            messages.success(request, _("Disease has been updated"))
            return redirect("app:check_disease", disease_id=disease.id)
    context = {"disease": disease, "animal": animal, "form": form}
    return render(request, "app/edit_disease.html", context)


@staff_member_required(login_url="app:index")
def edit_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    user_have_animal = False
    if appointment.service.admin_only == True:
        messages.success(request, _("You can not edit this appointment"))
        return redirect("app:appointment", appointment_id=appointment.id)
    if appointment.client:
        user = appointment.client
        client = User.objects.get(id=user.id)
        user_have_animal = Animal.objects.filter(owner=request.user)
    if request.method != "POST":
        if appointment.animal:
            form = AppointmentForm(
                instance=appointment, initial={"animal": appointment.animal}
            )
        else:
            form = AppointmentForm(instance=appointment)
            if appointment.client:
                form.fields["animal"] = forms.ModelChoiceField(
                    Animal.objects.filter(owner=appointment.client),
                    required=False,
                    empty_label="-----",
                )
    else:
        form = AppointmentForm(instance=appointment, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Information has been updated"))
            return redirect("app:appointment", appointment_id=appointment.id)
    context = {"appointment": appointment, "form": form}
    return render(request, "app/edit_appointment.html", context)
