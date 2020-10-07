import datetime
from app.models import Appointment
from user.models import Slot,Service
from datetime import timedelta 

def next_weekday(weekday,end_date):
    today = datetime.date.today()
    day = today.weekday()
    days_ahead = int(weekday) - int(day)
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    today = today + datetime.timedelta(days_ahead)
    dates = [today]
    while today < end_date:
        today = today + datetime.timedelta(days=7)
        dates.append(today)
    return dates

def weekdays(all_slots,week):
    slots=[]
    days=[]
    day = datetime.date.today()
    day = day + datetime.timedelta(days=-day.weekday(),weeks=week)
    for i in range(5):
        days.append(day+datetime.timedelta(days=i))
    for slot in all_slots:
        if slot.date in days:
            slots.append(slot)
    return slots

def what_week(week):
    day = datetime.date.today()
    day = day + datetime.timedelta(days=-day.weekday(),weeks=week)
    return [day,day+datetime.timedelta(days=6)]

def time_plus(time, timedelta):
    start = datetime.datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()

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