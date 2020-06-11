from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _, gettext_lazy as _lazy
from .models import Profile
from django.core.validators import RegexValidator

class DateInput(forms.DateInput):
    input_type = 'date'

class UserForm(UserCreationForm):
    first_name = forms.CharField(label=_lazy('First Name'),
                                validators=[RegexValidator(regex='^([A-ZŁŚĆĄŻŹÓĆŃĘ]){1}([a-zążźśęćńół]){2,30}$',
                                message=_lazy('Name should have first letter upper case and the rest lower case'))],
                                widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    last_name = forms.CharField(label=_lazy('Last Name'),
                                validators=[RegexValidator(regex='^([A-ZŁŚĆĄŻŹÓĆŃĘ]){1}([a-zążźśęćńół]){2,30}$',
                                message=_lazy('Surname should have first letter upper case and the rest lower case'))],
                                widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))                                               
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','first_name','last_name','email']
        widgets = {'username': forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}),
                   'email': forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

class ProfileForm(forms.ModelForm):
    city = forms.CharField(label=_lazy('City'),
                            validators=[RegexValidator(regex='^([A-ZŁŚĆĄŻŹÓĆŃĘ]{1}[a-zążźśęćńół]{1,20}(\-|\ ){0,1}){1,4}$',
                            message=_lazy('City should have first letter upper case and cannot contain special characters'))],
                            widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    phone_number = forms.CharField(label=_lazy('Phone number'),
                            validators=[RegexValidator(regex='^\+?1?\d{9,15}$',
                            message=_lazy("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))],
                            widget = forms.Textarea(attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))
    birth_date = forms.DateField(label=_lazy('Date of birth'),
                                widget=DateInput(format=('%Y-%m-%d'),attrs={'cols': 5, 'rows': 1,'class':'form-control','style':'resize:none;'}))                      
    class Meta:
        model = Profile
        fields = ('birth_date','city','phone_number')
        exclude=['user']

