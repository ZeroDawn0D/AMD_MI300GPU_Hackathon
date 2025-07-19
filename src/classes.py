class Event:
    def __init__(self, creator, start_time, end_time, subject, content):
        self.creator = creator
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.content = content
        self.window_start_time = None
        self.window_end_time = None
        self.priority = None
    # finish the rest as needed

    def to_dict(self):
        return {
            'creater': self.creator,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'subject': self.subject,
            'content': self.content
        }
    # Finish the rest as needed
