from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _,gettext_lazy as _lazy

class Profile(models.Model):
    user = models.OneToOneField(User,default=None, null=True, on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name=_lazy('phone_number'),
                                    max_length=15,
                                    blank=True,
                                    null=True,)
    city = models.CharField(verbose_name=_lazy('city'),
                            max_length=100,
                            blank=True,
                            null=True,)
    birth_date = models.DateField(null=True, blank=True)
