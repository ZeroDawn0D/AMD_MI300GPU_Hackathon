from classes import Event
from datetime import datetime
import json

def format_to_output(events,
                     new_event_dict: dict, 
                     new_event: Event) -> str:
    result_dict = {}

    result_dict["Request_id"] = new_event_dict["Request_id"]
    result_dict["Location"] = new_event_dict["Location"]
    result_dict["From"] = new_event_dict["From"]
    result_dict["Datetime"] = new_event_dict["Datetime"]
    result_dict["Subject"] = new_event_dict["Subject"]
    result_dict["EmailContent"] = new_event_dict["EmailContent"]
    result_dict["EventStart"] = new_event.final_start_time.isoformat()
    result_dict["EventEnd"] = new_event.final_end_time.isoformat()

    duration_secs = (new_event.final_end_time - new_event.final_start_time).total_seconds()
    result_dict["Duration_mins"] = duration_secs // 60
    result_dict["MetaData"] = {}

    user_to_timetable: dict[str, dict] = {}
    for event in events:
        user = event.creator
        if user not in user_to_timetable:
            user_to_timetable[user] = {
                "email": user,
                "events": []
            }
        
        user_to_timetable[user]["events"].append({
            "StartTime": event.final_start_time.isoformat(),
            "EndTime": event.final_end_time.isoformat(),
            "Attendees": event.attendees,
            "Summary": event.summary,
            "NumAttendees": len(event.attendees)
        })

    result_dict["Attendees"] = list(user_to_timetable.values())

    return json.dumps(result_dict)