from django.contrib import admin
from .models import Animal,Disease,Medicine, Appointment
from user.models import Profile, Doctor, Service, Slot
admin.site.register(Profile)
admin.site.register(Animal)
admin.site.register(Disease)
admin.site.register(Medicine)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Slot)