from datetime import timedelta

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from app.models import Appointment


class Profile(models.Model):
    user = models.OneToOneField(
        User, default=None, null=True, on_delete=models.CASCADE
    )
    phone_number = models.CharField(
        verbose_name=_lazy("phone_number"),
        max_length=15,
        blank=True,
        null=True,
    )
    city = models.CharField(
        verbose_name=_lazy("city"),
        max_length=100,
        blank=True,
        null=True,
    )
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Service(models.Model):
    name = models.CharField(
        verbose_name=_lazy("service"), max_length=200, null=True
    )
    duration = models.DurationField(verbose_name=_lazy("duration"), null=True)
    admin_only = models.BooleanField(
        null=True, verbose_name=_lazy("staff only")
    )

    class Meta:
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.name}"


class Doctor(models.Model):
    profile = models.OneToOneField(
        Profile,
        verbose_name=_lazy("profile"),
        default=None,
        on_delete=models.CASCADE,
    )
    speciality = models.CharField(
        verbose_name=_lazy("speciality"), max_length=50
    )
    image = models.ImageField(upload_to="static/profile_images", blank=True)
    services = models.ManyToManyField(Service, verbose_name=_lazy("services"))

    class Meta:
        verbose_name_plural = "Doctors"

    def __str__(self):
        return f"{self.profile.user.first_name} {self.profile.user.last_name}"


class Slot(models.Model):
    doctor = models.ForeignKey(
        Doctor, verbose_name=_lazy("doctor"), on_delete=models.CASCADE
    )
    date = models.DateField(verbose_name=_lazy("date"), null=True)
    start_time = models.TimeField(verbose_name=_lazy("start time"), null=True)
    end_time = models.TimeField(verbose_name=_lazy("end time"), null=True)

    class Meta:
        verbose_name_plural = "Slots"

    def __str__(self):
        return f"{self.doctor} - {self.date}"
