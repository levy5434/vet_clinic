from django import template
from django.contrib.auth.models import Group 
from user.models import Slot,Service
from app.models import Appointment
from app.functions import time_plus
from datetime import timedelta

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name)
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False

@register.simple_tag(name='check_appointments')
def check_appointments(slot_id):
    slot = Slot.objects.get(id=slot_id)
    if Appointment.objects.filter(slot=slot):
        return True
    return False

@register.simple_tag(name='free_hours')
def free_hours(slot_id,service_id):
    slot = Slot.objects.get(id=slot_id)
    service = Service.objects.get(id=service_id)
    service_duration_parts = int(((service.duration/15).seconds)/60) #15minutes 60seconds
    appointments = Appointment.objects.filter(slot=slot)
    start = slot.start_time
    times = []
    while start < slot.end_time:
        times.append(start)
        start = time_plus(start, timedelta(minutes=15))
    for appointment in appointments:
        t = appointment.start_time
        while t < time_plus(appointment.start_time,appointment.service.duration):
            if t in times:
                times.remove(t)
            t = time_plus(t, timedelta(minutes=15))     
    if service_duration_parts > 1:
        times.append(time_plus(times[len(times)-1],timedelta(minutes=15)))
        free_times = []
        for x in range(len(times) - service_duration_parts):
            time = times[x]
            end_time = time_plus(time, service.duration) # end time of the visit if time[x]
            if times[x+service_duration_parts] == end_time:
                free_times.append(time)
        return free_times            
    return times    