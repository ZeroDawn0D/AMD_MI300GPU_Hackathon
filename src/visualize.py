from datetime import datetime, timedelta

def draw_timeline(start_datetime, end_datetime, suffix):
    time = datetime.combine(start_datetime.date(), datetime.min.time()) + timedelta(hours=9)
    end = datetime.combine(end_datetime.date(), datetime.min.time()) + timedelta(hours=17)

    timeline = ""
    current = time
    while current < end:
        if start_datetime <= current < end_datetime:
            timeline += "#"
        else:
            timeline += "-"
        current += timedelta(minutes=30)
    
    print(timeline + f" ({suffix})")