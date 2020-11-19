import datetime
from app.models import Appointment
from user.models import Slot,Service
from datetime import timedelta, datetime, date

def next_weekday(weekday,start_date,end_date):
    today = start_date
    days_ahead = int(weekday) - int(today.weekday())
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    today = today + timedelta(days_ahead)
    dates = [today]
    while today < end_date:
        today = today + timedelta(days=7)
        dates.append(today)
    return dates

def what_week(week):
    day = date.today()
    day = day + timedelta(days=-day.weekday(),weeks=week)
    day2 = day + timedelta(days=6)
    return [day,day2]

def whole_week(week):
    day = date.today()
    day = day + timedelta(days=-day.weekday(),weeks=week)
    days = []
    for i in range(7):
        days.append(day+timedelta(days=i))
    return days    

def time_plus(time, delta):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + delta
    return end.time()

def free_hours(slot_id,service_id):
    slot = Slot.objects.get(id=slot_id)
    service = Service.objects.get(id=service_id)
    service_duration_parts = int(((service.duration/15).seconds)/60) #15minutes 60seconds
    appointments = Appointment.objects.filter(slot=slot).order_by('start_time')
    start = slot.start_time
    times = []
    now = datetime.now().time()
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

def scheduler(slot_id):
    slot = Slot.objects.get(id=slot_id)
    appointments = Appointment.objects.filter(slot=slot).order_by('start_time')
    start = slot.start_time
    times = []
    times1 = []
    while start < slot.end_time:
        times.append(start)
        start = time_plus(start, timedelta(minutes=15))
    all_times = times.copy()    
    for appointment in appointments:
        for i in range(len(times)):
            if appointment.start_time == times[i]:
                times[i] = [times[i],appointment]        
                break
    i = 0
    while i < len(times):
        if type(times[i])==list:
            parts = int(((times[i][1].service.duration/15).seconds)/60)
            times1.append([times[i][1],parts])
            i=i+parts
        else:
            times1.append([0,1])
            i=i+1           
    return all_times,times1     

