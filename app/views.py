from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Animal, Disease, Medicine, Appointment
from .forms import AnimalForm, DiseaseForm, MedicineForm, SlotForm, AppointmentForm, DayForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from user.models import Profile, Doctor, Service, Slot
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import unauthenticated_user, allowed_users
from datetime import datetime,date,timedelta,time
from .functions import next_weekday, weekdays, what_week, time_plus,free_hours
from django import forms
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def index(request):
    if request.user.groups.filter(name__in=['Admin']).exists():
        appointments = Appointment.objects.filter(slot__isnull=True).exists()
        print(appointments)
        if appointments:
            no_slot_appointments = True
            context = {'no_slot_appointments':no_slot_appointments}
            return render(request, 'app/index.html',context)
    return render(request, 'app/index.html')

def doctor(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    all_slots = doctor.slot_set.all().order_by('date')
    slots = weekdays(all_slots,1)
    context = {'doctor': doctor,'slots':slots}
    return render(request, 'app/doctor.html', context)   

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('date','start_time')
    upcoming_appointment = []
    today = date.today()
    for appointment in appointments:
        if appointment.date >= today:
            upcoming_appointment = appointment
            appointments = appointments.exclude(id=upcoming_appointment.id)
            break
    context = {'appointments': appointments,'upcoming_appointment':upcoming_appointment}
    return render(request, 'app/my_appointments.html', context)

@login_required
def make_appointment(request):
    services = Service.objects.all()
    context = {'services':services}
    return render(request, 'app/make_appointment.html', context)

@login_required
def appointment(request,appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    client = appointment.client
    delete = False
    if appointment.date > date.today():
        delete = True
    if request.user != client and not request.user.is_staff:
        raise PermissionDenied
    context = {'appointment':appointment,'delete':delete}
    return render(request, 'app/appointment.html', context)

@login_required
def make_appointment_d(request,service_id):
    services = Service.objects.all().exclude(id=service_id)
    my_service = Service.objects.get(id=service_id)
    doctors = Doctor.objects.filter(services__id=service_id)
    context = {'services':services,'my_service':my_service,'doctors':doctors}
    return render(request, 'app/make_appointment_d.html', context)

@login_required
def make_appointment_s(request,service_id,doctor_id,week):
    services = Service.objects.all().exclude(id=service_id)
    my_service = Service.objects.get(id=service_id)
    selected_doctor = Doctor.objects.get(id=doctor_id)
    all_slots = Slot.objects.filter(doctor=selected_doctor).order_by('date')
    slots = weekdays(all_slots,week)
    n_week = week+1
    p_week = week-1
    first = what_week(week)[0]
    last = what_week(week)[1]
    doctors = Doctor.objects.filter(services__id=service_id).exclude(id=doctor_id)
    context = {'services':services,'my_service':my_service,
                'doctors':doctors,'selected_doctor':selected_doctor, 'slots':slots,
                'week':week,'n_week':n_week,'p_week':p_week,'first':first,'last':last}
    return render(request, 'app/make_appointment_s.html', context)

@login_required
def make_appointment_f(request,service_id,slot_id,time):
    service = Service.objects.get(id=service_id)
    slot = Slot.objects.get(id=slot_id)
    times = free_hours(slot.id,service.id)
    doctor = slot.doctor
    if not doctor.services.filter(id=service.id).exists():
        messages.success(request, 'This service is not available!')
        return redirect('app:make_appointment_s', service_id=service.id,doctor_id=doctor.id,week=0)
    available = False
    for f_time in times:
        if time == f_time.strftime("%H:%M:%S"):
            available = True
    if available == False:
        messages.success(request, 'This hour is not available!')
        return redirect('app:make_appointment_s', service_id=service.id,doctor_id=doctor.id,week=0)
    user = User.objects.get(username=request.user.username)
    user_have_animal = Animal.objects.filter(owner=request.user)
    if request.method!='POST':
        if user_have_animal:
            form = AppointmentForm(initial={'animal':user_have_animal[0]})
        else: 
            form = AppointmentForm()    
        form.fields['animal'] = forms.ModelChoiceField(Animal.objects.filter(owner=request.user)
                                                        ,required=False,empty_label="New Pet")
    else:
        form = AppointmentForm(request.POST)
        if form.is_valid():
            if request.POST['animal']:
                animal = Animal.objects.get(id=request.POST['animal'])
                appointment = Appointment(client = user,
                                            animal = animal, 
                                            service = service,
                                            doctor = doctor,
                                            slot=slot,
                                            date = slot.date, 
                                            start_time = time,
                                            information=request.POST['information']
                                            )
            else:
                text = f"Name: {request.POST['name']} \n Specie: {request.POST['specie']} \n "
                text = text + request.POST['information']
                appointment = Appointment(client = user,
                            service = service,
                            slot=slot,
                            doctor = doctor,
                            date = slot.date, 
                            start_time = time,
                            information=text
                            )
            appointment.save()
            messages.success(request, 'Success! Appointment has been booked.')
            return redirect('app:my_appointments') 
    context = {'form':form,'service':service,'slot':slot,'doctor':doctor,'time':time,'user_have_animal':user_have_animal}
    return render(request,'app/make_appointment_f.html',context)


@login_required
def delete_appointment(request,appointment_id):
    appointment = get_object_or_404(Appointment,id=appointment_id)
    if appointment.date <= date.today():
        messages.success(request, 'You can not delete previous appointments')
        return redirect('app:my_appointments')
    user = appointment.client
    if request.user != user and not request.user.groups.filter(name__in=['Admin']).exists():
        raise PermissionDenied
    if request.method == "POST":
        appointment.delete()
        messages.success(request, 'Appointment has been deleted')
        return redirect('app:my_appointments')
    context = {'appointment':appointment}    
    return render(request,"app/delete_appointment.html",context)    

def doctors(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render (request,'app/doctors.html', context)

@login_required
def animals(request):
    animals= Animal.objects.filter(owner=request.user).order_by('register_date')
    if animals.count()==1:
        return redirect('app:disease',animal_id=animals[0].id)
    context = {'animals': animals}
    return render(request, 'app/animals.html', context)

@login_required
def appointment(request,appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    context = {'appointment': appointment}
    return render(request, 'app/appointment.html', context)
    
@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def my_schedule(request,week):
    profile = Profile.objects.get(user=request.user.id)
    doctor = Doctor.objects.get(profile = profile) 
    all_slots = doctor.slot_set.all().order_by('date')
    slots = weekdays(all_slots,week)
    n_week = week + 1
    p_week = week - 1
    today = []
    first = what_week(week)[0]
    last = what_week(week)[1]
    for slot in slots:
        if slot.date == date.today():
            today = slot
    if today:
        
        context = {'slots': slots, 'today':today,'week':week,'n_week':n_week,'p_week':p_week,'first':first,'last':last}
    else:
        today_free = date.today()
        context = {'slots': slots,'today_free':today_free,'week':week,'n_week':n_week,'p_week':p_week,'first':first,'last':last}
    return render(request, 'app/my_schedule.html', context)
     
@login_required
def disease(request,animal_id):
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
    
    context = {'animal':animal,'actual_diseases': actual_diseases,'client':client,'past_diseases':past_diseases,'appointments':appointments}
    return render(request, 'app/disease.html', context)

@login_required
def check_disease(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    medicines = disease.medicine_set.all()
    animal = disease.animal
    client = animal.owner
    if request.user != client and not request.user.is_staff:
        raise PermissionDenied
    context = {'disease': disease,'medicines':medicines,'animal':animal}
    return render(request, 'app/check_disease.html', context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def add_pet(request,client_id):
    client = User.objects.get(id=client_id)
    if request.method!='POST':
        form = AnimalForm()
    else:
        form = AnimalForm(data=request.POST)
        if form.is_valid():
            new_pet = form.save(commit=False)
            new_pet.owner = client
            new_pet.save()
            return redirect('app:client', client_id=client_id) 
    context = {'form':form,'client':client}
    return render(request,'app/add_pet.html',context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def browse_clients(request):
    clients = User.objects.all()
    query = request.GET.get("q")
    if query:
        clients = clients.filter(last_name__icontains=query)
    context = {'clients':clients}
    return render(request, 'app/browse_clients.html', context)    

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def client(request,client_id):
    client = User.objects.get(id=client_id)
    animals = client.animal_set.all()
    context = {'client':client,'animals': animals}
    return render(request, 'app/client.html', context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def appointments_to_reschedule(request):
    appointments = Appointment.objects.filter(slot__isnull=True)
    context = {'appointments':appointments}
    return render(request, 'app/appointments_to_reschedule.html', context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def add_disease(request,pet_id):
    pet = Animal.objects.get(id=pet_id)
    if request.method!='POST':
        form = DiseaseForm()
    else:
        form = DiseaseForm(data=request.POST)
        if form.is_valid():
            new_disease = form.save(commit=False)
            new_disease.animal = pet
            new_disease.save()
            return redirect('app:disease',disease_id=disease.id) 
    context = {'form':form,'pet':pet}
    return render(request,'app/add_disease.html',context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def pet_delete(request,pet_id):
    pet = get_object_or_404(Animal,id=pet_id)
    client = pet.owner
    if request.method == "POST":
        pet.delete()
        return redirect('app:client', client_id=client.id)
    context = {'client':client,'pet':pet}    
    return render(request,"app/delete_pet.html",context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def manage_slots(request,doctor_id,week):
    doctor = Doctor.objects.get(id=doctor_id)
    all_slots = Slot.objects.filter(doctor=doctor).order_by('date')
    slots = weekdays(all_slots,week)
    n_week = week+1
    p_week = week-1
    first = what_week(week)[0]
    last = what_week(week)[1]
    context = {'doctor':doctor,'slots':slots,'week':week,'n_week':n_week,'p_week':p_week,
                'first':first,'last':last}
    return render(request, 'app/manage_slots.html', context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def delete_slot(request,slot_id):
    slot = get_object_or_404(Slot,id=slot_id)
    doctor = slot.doctor
    if request.method == "POST":
        slot.delete()
        return redirect('app:manage_slots', doctor_id=doctor.id, week=0)
    context = {'slot':slot,'doctor':doctor}    
    return render(request,"app/delete_slot.html",context)

@staff_member_required(login_url='app:index')
def slot(request, slot_id):
    slot = Slot.objects.get(id=slot_id)
    doctor = slot.doctor
    profile = doctor.profile
    user = profile.user
    if request.user != user and not request.user.groups.filter(name__in=['Admin']).exists():
        raise PermissionDenied
    appointments = Appointment.objects.filter(slot=slot).order_by('start_time')
    upcoming_appointment = []
    if date.today() == slot.date:
        now = datetime.now().time()
    else:
        now = time(5,0,0)   
    for appointment in appointments:
        if now <= time_plus(appointment.start_time,appointment.service.duration):
            upcoming_appointment = appointment
            appointments = appointments.exclude(id=upcoming_appointment.id)
            break
    context = {'slot': slot,'appointments':appointments,'upcoming_appointment':upcoming_appointment}
    return render(request, 'app/slot.html', context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def add_medicine(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    animal = disease.animal
    if request.method!='POST':
        form = MedicineForm()
    else:
        form = MedicineForm(data=request.POST)
        if form.is_valid():
            new_medicine = form.save(commit=False)
            new_medicine.disease = disease
            new_medicine.save()
            return redirect('app:check_disease',disease_id=disease.id) 
    context = {'form':form,'disease':disease,'animal':animal}
    return render(request,'app/add_medicine.html',context)    

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Admin'])
def add_slot(request,doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    all_slots = doctor.slot_set.all().order_by('date')
    slots = weekdays(all_slots,1)
    if request.method != 'POST':
        day_form = DayForm()
        slot_form = SlotForm()
    else:
        slot_form = SlotForm(request.POST)
        day_form = DayForm(request.POST)
        if slot_form.is_valid() and day_form.is_valid():
            day = day_form.cleaned_data.get('day')
            end_date = day_form.cleaned_data.get('end_date')
            dates = next_weekday(day,end_date)
            for date in dates:
                slot = Slot(doctor= doctor,
                            date = date,
                            start_time = request.POST['start_time'],
                            end_time = request.POST['end_time'],
                            )
                slot.save()
            return redirect('app:doctor',doctor_id=doctor.id) 
    context = {'slot_form': slot_form,'day_form':day_form,'doctor':doctor,'slots':slots} 
    return render(request, 'app/add_slot.html', context)    

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def edit_medicine(request,medicine_id):
    medicine = Medicine.objects.get(id=medicine_id)
    disease = medicine.disease
    if request.method!='POST':
        form = MedicineForm(instance=medicine)
    else:
        form = MedicineForm(instance=medicine, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:check_disease',disease_id=disease.id)    
    context ={'disease':disease,'medicine':medicine,'form':form}
    return render(request,'app/edit_medicine.html',context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def medicine_delete(request,medicine_id):
    medicine = get_object_or_404(Medicine,id=medicine_id)
    disease = medicine.disease
    if request.method == "POST":
        medicine.delete()
        return redirect('app:check_disease',disease_id=disease.id)
    context = {'disease':disease,'medicine':medicine}    
    return render(request,"app/delete_medicine.html",context)

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def disease_delete(request,disease_id):
    disease = get_object_or_404(Disease,id=disease_id)
    pet = disease.animal
    if request.method == "POST":
        disease.delete()
        return redirect('app:disease',animal_id=pet.id)
    context = {'disease':disease,'pet':pet}    
    return render(request,"app/delete_disease.html",context)    

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def edit_disease(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    animal = disease.animal
    if request.method!='POST':
        form = DiseaseForm(instance=disease)
    else:
        form = DiseaseForm(instance=disease, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:check_disease',disease_id=disease.id)    
    context ={'disease':disease,'animal':animal,'form':form}
    return render(request,'app/edit_disease.html',context)  

@staff_member_required(login_url='app:index')
@allowed_users(allowed_roles=['Doctors'])
def edit_appointment(request,appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method!='POST':
        form = AppointmentForm(instance=appointment,initial={'animal':appointment.animal})
    else:
        form = AppointmentForm(instance=appointment, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:appointment',appointment_id=appointment.id)    
    context ={'appointment':appointment,'form':form}
    return render(request,'app/edit_appointment.html',context)  