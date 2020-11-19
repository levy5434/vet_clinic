from django import template
from django.contrib.auth.models import Group 
from user.models import Slot,Service
from app.models import Appointment
from app.functions import time_plus
from datetime import timedelta,datetime
from datetime import date

register = template.Library() 

@register.filter(name='times') 
def times(number):
    return range(number)

@register.filter
def lookup(d, key):
    return d[key]

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
    appointments = Appointment.objects.filter(slot=slot).order_by('start_time')
    start = slot.start_time
    now = datetime.now().time()
    times = []
    if slot.date < date.today():
        return times
    if start < now and slot.date == date.today():
        current_minutes = int(now.strftime("%M"))
        current_seconds = int(now.strftime("%S"))
        rest = 15 - (current_minutes%15)
        start = time_plus(now,timedelta(minutes=(rest+60),seconds=(-current_seconds)))
    else:    
        start = slot.start_time
    while start < slot.end_time:
        times.append(start)
        start = time_plus(start, timedelta(minutes=15))
    if times:
        for appointment in appointments:
            t = appointment.start_time
            while t < time_plus(appointment.start_time,appointment.service.duration):
                if t in times:
                    times.remove(t)
                t = time_plus(t, timedelta(minutes=15))
        if service_duration_parts > 1:
            free_times = []
            service_duration_parts = service_duration_parts - 1
            for x in range(len(times) - service_duration_parts):
                time = times[x]
                end_time = time_plus(time, timedelta(minutes=(15*service_duration_parts))) # end time of the visit if time[x]
                if times[x+service_duration_parts] == end_time:
                    free_times.append(time)
            start = slot.start_time
            times2 = []
            while start < slot.end_time:
                if start in free_times:
                    times2.append(start)
                start = time_plus(start, timedelta(minutes=15*(service_duration_parts+1)))        
            return times2      
    return times    