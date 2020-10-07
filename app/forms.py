from django import forms
from .models import Animal,Disease,Medicine, Appointment
from user.models import Slot
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
                'register_date':DateInput(format=('%Y-%m-%d')),'cure_data':DateInput(format=('%m-%d-%Y'))}

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','dose','status','introduction_date','end_data']
        widgets= {'introduction_date':DateInput(format=('%Y-%m-%d')),'end_data':DateInput(format=('%Y-%m-%d'),attrs={
                'class': 'datepicker'
            })}

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ['start_time','end_time']
        widgets= {'start_time':forms.TimeInput(attrs={'type': 'time'}),
                    'end_time':forms.TimeInput(attrs={'type': 'time'})}

class DayForm(forms.Form):
    DAY_CHOICES = (
        (0,'Monday'),
        (1,'Tuesday'),
        (2,'Wednesday'),
        (3,'Thursday'),
        (4,'Friday'),
        (5,'Saturday'),
        (6,'Sunday')
    )
    day = forms.ChoiceField(choices=DAY_CHOICES)
    end_date = forms.DateField(widget=DateInput(format=('%Y-%m-%d')))

class AppointmentForm(forms.ModelForm):
    name = forms.CharField(label=_lazy('Name'),required=False)
    specie = forms.CharField(label=_lazy('Specie'),required=False)
    class Meta:
        model = Appointment
        fields = ['animal','information']
        widgets= {'information':forms.Textarea(attrs={'cols': 40, 'rows': 4,'class':'form-control','style':'resize:none;'})}
                