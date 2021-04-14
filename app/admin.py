from django.contrib import admin

from user.models import Doctor, Profile, Service, Slot

from .models import Animal, Appointment, Disease, Medicine

admin.site.register(Profile)
admin.site.register(Animal)
admin.site.register(Disease)
admin.site.register(Medicine)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Slot)
