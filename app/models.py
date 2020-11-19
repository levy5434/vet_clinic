from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext as _,gettext_lazy as _lazy
#from user.models import Doctor,Service,Slot

class Animal(models.Model):
    name = models.CharField(verbose_name=_lazy('name'),max_length=20)
    specie = models.CharField(verbose_name=_lazy('specie'),max_length=20)
    birth_date = models.DateField(verbose_name=_lazy('birth date'),auto_now_add=False,null=True)
    register_date = models.DateField(verbose_name=_lazy('register date'),auto_now_add=True)
    owner = models.ForeignKey(User,verbose_name=_lazy('owner'), on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'Animals'
    def __str__(self):
        return f"{self.name}, {self.specie}"

class Disease(models.Model):
    animal = models.ForeignKey(Animal,verbose_name=_lazy('animal'), on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_lazy('name'),max_length=60)
    recommendations = models.TextField(verbose_name=_lazy('recommendations'),)
    register_date = models.DateField(verbose_name=_lazy('register date'),null=True)
    status = models.BooleanField(null=True)
    cure_data = models.DateField(verbose_name=_lazy('cure date'),null=True,blank=True)
    doctor = models.CharField(verbose_name=_lazy('name'),max_length=40,null=True,blank=True)
    class Meta:
        verbose_name_plural = 'Diseases'
    def __str__(self):
        return f"{self.name}"

class Medicine(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_lazy('name'),max_length=40)
    dose = models.CharField(verbose_name=_lazy('dose'),max_length=60)
    introduction_date = models.DateField(verbose_name=_lazy('introduction date'),null=True) 
    status = models.BooleanField(null=True)
    end_data = models.DateField(verbose_name=_lazy('end date'),null=True,blank=True)
    doctor = models.CharField(verbose_name=_lazy('doctor'),max_length=40,null=True,blank=True)
    class Meta:
        verbose_name_plural = 'Medicines'
    def __str__(self):
        return f"{self.name}"

class Appointment(models.Model):
    client = models.ForeignKey(User,verbose_name=_lazy('client'),null=True, default=None, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal,verbose_name=_lazy('animal'), on_delete=models.CASCADE,blank=True,null=True)
    slot = models.ForeignKey('user.Slot',verbose_name=_lazy('slot'), null=True, on_delete=models.SET_NULL)
    service = models.ForeignKey('user.Service',verbose_name=_lazy('service'), null=True, on_delete=models.SET_NULL)
    doctor = models.ForeignKey('user.Doctor',verbose_name=_lazy('doctor'), null=True, on_delete=models.SET_NULL)
    date = models.DateField(verbose_name=_lazy('date'),null=True)
    start_time = models.TimeField(verbose_name=_lazy('start time'),null=True)
    information = models.TextField(verbose_name=_lazy('information'),null=True,blank=True)
    class Meta:
        verbose_name_plural = 'Appointments'
    def __str__(self):
        return f"{self.animal} - {self.service} - {self.doctor}"