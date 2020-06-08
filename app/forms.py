from django import forms
from .models import Animal,Disease,Medicine
from django.utils.translation import gettext as _

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name','specie','birth_date']

class DiseaseForm(forms.ModelForm): 
    class Meta:
        model = Disease
        fields = ['name','recommendations','status','register_date','cure_data']
        labels = {'status':'Active'}
        widgets = {'recommendations': forms.Textarea(attrs={'cols': 40, 'rows': 4,'class':'form-control','style':'resize:none;'})}

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','dose','status','introduction_date','end_data']