from django import forms
from .models import Animal,Disease,Medicine, Appointment
from user.models import Slot
from django.utils.translation import gettext_lazy as _lazy
from django.core.validators import RegexValidator
from django.utils.functional import lazy

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
        (6,'Sunday'),
    )
    #day = forms.ChoiceField(choices=lazy(DAY_CHOICES, tuple)())
    day = forms.ChoiceField(choices=DAY_CHOICES)
    start_date = forms.DateField(widget=DateInput(format=('%Y-%m-%d')))
    end_date = forms.DateField(widget=DateInput(format=('%Y-%m-%d')))

class AppointmentForm(forms.ModelForm):
    name = forms.CharField(label=_lazy('Name'),required=False)
    client_first_name = forms.CharField(label=_lazy('First Name'),
                                required=False,
                                validators=[RegexValidator(regex='^([A-ZŁŚĆĄŻŹÓĆŃĘ]){1}([a-zążźśęćńół]){2,30}$',
                                message=_lazy('Name should have first letter upper case and the rest lower case'))],
                                widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    client_last_name = forms.CharField(label=_lazy('Last Name'),
                                required=False,
                                validators=[RegexValidator(regex='^([A-ZŁŚĆĄŻŹÓĆŃĘ]){1}([a-zążźśęćńół]){2,30}$',
                                message=_lazy('Surname should have first letter upper case and the rest lower case'))],
                                widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    client_phone = forms.CharField(label=_lazy('Phone number'),
                            required=False,
                            validators=[RegexValidator(regex='^\+?1?\d{9,15}$',
                            message=_lazy("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))],
                            widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    name = forms.CharField(label=_lazy('Name'),required=False)
    species = forms.CharField(label=_lazy('Species'),required=False)
    class Meta:
        model = Appointment
        fields = ['animal','information']
        widgets= {'information':forms.Textarea(attrs={'cols': 40, 'rows': 4,'class':'form-control','style':'resize:none;'})}
                