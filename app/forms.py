from django import forms
from .models import Animal,Disease,Medicine
from django.utils.translation import gettext_lazy as _lazy

class DateInput(forms.DateInput):
    input_type = 'date'

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name','specie','birth_date']
        widgets = {'birth_date':DateInput(format=('%Y-%m-%d')),}

class DiseaseForm(forms.ModelForm): 
    class Meta:
        model = Disease
        fields = ['name','recommendations','status','register_date','cure_data']
        labels = {'status':_lazy('Active')}
        widgets = {'recommendations': forms.Textarea(attrs={'cols': 40, 'rows': 4,'class':'form-control','style':'resize:none;'}),
                'register_date':DateInput(format=('%Y-%m-%d')),'cure_data':DateInput(format=('%Y-%m-%d'))}

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','dose','status','introduction_date','end_data']
        widgets= {'introduction_date':DateInput(format=('%Y-%m-%d')),'end_data':DateInput(format=('%Y-%m-%d'))}