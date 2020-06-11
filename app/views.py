from django.shortcuts import render,redirect
from django.urls import reverse
from .models import Animal, Disease,Medicine
from .forms import AnimalForm,DiseaseForm,MedicineForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from user.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

def index(request):
    return render(request, 'app/index.html')

@login_required
def animals(request):
    animals= Animal.objects.filter(owner=request.user).order_by('register_date')
    context = {'animals': animals}
    return render(request, 'app/animals.html', context)   

@login_required
def disease(request,animal_id):
    animal = Animal.objects.get(id=animal_id)
    diseases= animal.disease_set.all()
    actual_diseases = []
    past_diseases = []
    for disease in diseases:
        if disease.status == False:
            past_diseases.append(disease)
        else:
            actual_diseases.append(disease)
    client = animal.owner
    context = {'animal':animal,'actual_diseases': actual_diseases,'client':client,'past_diseases':past_diseases}
    return render(request, 'app/disease.html', context)

@login_required
def check_disease(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    medicines = disease.medicine_set.all()
    animal = disease.animal
    context = {'disease': disease,'medicines':medicines,'animal':animal}
    return render(request, 'app/check_disease.html', context)

@staff_member_required(login_url='app:index')
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
def browse_clients(request):
    clients = User.objects.all()
    query = request.GET.get("q")
    if query:
        clients = clients.filter(last_name__icontains=query)
    context = {'clients':clients}
    return render(request, 'app/browse_clients.html', context)    

@staff_member_required(login_url='app:index')
def client(request,client_id):
    client = User.objects.get(id=client_id)
    animals = client.animal_set.all()
    context = {'client':client,'animals': animals}
    return render(request, 'app/client.html', context)

@staff_member_required(login_url='app:index')
def pet(request,pet_id):
    pet = Animal.objects.get(id=pet_id)
    client = pet.owner
    diseases= pet.disease_set.all()
    actual_diseases = []
    past_diseases = []
    for disease in diseases:
        if disease.status == False:
            past_diseases.append(disease)
        else:
            actual_diseases.append(disease)
    context = {'pet':pet,'actual_diseases': actual_diseases,'past_diseases': past_diseases,'client':client}
    return render(request, 'app/pet.html', context)

@staff_member_required(login_url='app:index')
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
            return redirect('app:pet', pet_id=pet_id) 
    context = {'form':form,'pet':pet}
    return render(request,'app/add_disease.html',context)

@staff_member_required(login_url='app:index')
def pet_delete(request,pet_id):
    pet = get_object_or_404(Animal,id=pet_id)
    client = pet.owner
    if request.method == "POST":
        pet.delete()
        return redirect('app:client', client_id=client.id)
    context = {'client':client,'pet':pet}    
    return render(request,"app/delete_pet.html",context)

@staff_member_required(login_url='app:index')
def pet_disease(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    pet = disease.animal
    medicines = disease.medicine_set.all()
    context = {'disease': disease,'medicines':medicines,'pet':pet}
    return render(request, 'app/pet_disease.html', context)

@staff_member_required(login_url='app:index')
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
            return redirect('app:pet_disease', disease_id=disease.id) 
    context = {'form':form,'disease':disease,'animal':animal}
    return render(request,'app/add_medicine.html',context)    

@staff_member_required(login_url='app:index')
def edit_medicine(request,medicine_id):
    medicine = Medicine.objects.get(id=medicine_id)
    disease = medicine.disease
    if request.method!='POST':
        form = MedicineForm(instance=medicine)
    else:
        form = MedicineForm(instance=medicine, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:pet_disease',disease_id=disease.id)    
    context ={'disease':disease,'medicine':medicine,'form':form}
    return render(request,'app/edit_medicine.html',context)

@staff_member_required(login_url='app:index')
def medicine_delete(request,medicine_id):
    medicine = get_object_or_404(Medicine,id=medicine_id)
    disease = medicine.disease
    if request.method == "POST":
        medicine.delete()
        return redirect('app:pet_disease', disease_id=disease.id)
    context = {'disease':disease,'medicine':medicine}    
    return render(request,"app/delete_medicine.html",context)

@staff_member_required(login_url='app:index')
def disease_delete(request,disease_id):
    disease = get_object_or_404(Disease,id=disease_id)
    pet = disease.animal
    if request.method == "POST":
        disease.delete()
        return redirect('app:pet', pet_id=pet.id)
    context = {'disease':disease,'pet':pet}    
    return render(request,"app/delete_disease.html",context)    

@staff_member_required(login_url='app:index')
def edit_disease(request,disease_id):
    disease = Disease.objects.get(id=disease_id)
    animal = disease.animal
    if request.method!='POST':
        form = DiseaseForm(instance=disease)
    else:
        form = DiseaseForm(instance=disease, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:pet_disease',disease_id=disease.id)    
    context ={'disease':disease,'animal':animal,'form':form}
    return render(request,'app/edit_disease.html',context)  