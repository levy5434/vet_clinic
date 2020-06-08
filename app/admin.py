from django.contrib import admin
from .models import Animal,Disease,Medicine
from user.models import Profile
admin.site.register(Profile)
admin.site.register(Animal)
admin.site.register(Disease)
admin.site.register(Medicine)