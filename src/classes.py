from datetime import datetime, time

class Event:
    def __init__(self, creator: str,start_time: datetime, end_time: datetime,
                 summary: str, attendees: list[str], priority=None):
        
        # Fields initialized at the creation of the event
        self.creator = creator
        self.start_time = start_time
        self.end_time = end_time
        self.summary = summary
        self.attendees = attendees

        # Fields initialized later in the pipeline, for now set to default values
        curr_time = datetime.now()
        if priority:
            self.priority = priority
        else:
            self.priority: float = 0.0
        self.window_start_time: datetime = datetime.combine(curr_time.date(), time(9, 0)) 
        self.window_end_time: datetime = datetime.combine(curr_time.date(), time(17, 0))
        self.final_start_time: datetime = curr_time
        self.final_end_time: datetime = curr_time

    def to_dict(self):
        return {
            'creater': self.creator,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'summary': self.summary,
        }
    # Finish the rest as needed
