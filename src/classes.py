from datetime import datetime

class Event:
    def __init__(self, creator: str, start_time: datetime, end_time: datetime,
                 summary: str, attendees: list[str]):
        
        # Fields initialized at the creation of the event
        self.creator = creator
        self.start_time = start_time
        self.end_time = end_time
        self.summary = summary
        self.attendees = attendees

        # Fields initialized later in the pipeline
        self.window_start_time = None
        self.window_end_time = None
        self.priority = None
        self.final_start_time = None
        self.final_end_time = None

    def to_dict(self):
        return {
            'creater': self.creator,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'summary': self.summary,
        }
    # Finish the rest as needed
