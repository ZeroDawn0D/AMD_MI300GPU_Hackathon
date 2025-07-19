from datetime import datetime

class Event:
    def __init__(self, request_id: int, creator: str, start_time: datetime,
                 end_time: datetime, subject: str, content: str,
                 attendees: list[str]):
        
        # Fields initialized at the creation of the event
        self.request_id = request_id
        self.creator = creator
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.content = content
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
            'subject': self.subject,
            'content': self.content
        }
    # Finish the rest as needed
