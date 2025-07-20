from flask import Flask, request, jsonify
from threading import Thread
import json
from src.calendar_priority import set_event_priorities_sync
from src.calendar_events import get_all_calendar_events
from src.output import format_to_output
from src.classes import Event
from datetime import datetime, timedelta, timezone
from src.scheduling.interval_tree import reschedule_all_meetings


app = Flask(__name__)

users = [
    "userone.amd@gmail.com",
    "usertwo.amd@gmail.com",
    "userthree.amd@gmail.com"
]

# Dummy function to simulate getting a new event from a dict
def get_new_event_from_dict():
    new_event = Event(
        "userone.amd@gmail.com",
        datetime.fromisoformat("2025-07-22T10:00:00+05:30"), datetime.fromisoformat("2025-07-22T10:30:00+05:30"),
        "Hiking with friends", [ "usertwo.amd@gmail.com", "userthree.amd@gmail.com" ]
    )

    new_event.window_start_time = datetime.fromisoformat("2025-07-22T10:00:00+05:30")
    new_event.window_end_time = datetime.fromisoformat("2025-07-23T10:00:00+05:30")

    return new_event


def your_meeting_assistant(data): 
    # Get new event details from the incoming dict
    # will come from Rohit
    new_event = get_new_event_from_dict()
    ist = timezone(timedelta(hours=5, minutes=30))
    curr_time = datetime.now(ist)
    calender_events = get_all_calendar_events(users, curr_time.isoformat(), 
                                                (curr_time + timedelta(weeks=1)).isoformat())
    calender_events.append(new_event)
    set_event_priorities_sync(calender_events)
    # use new_event and calender_events to get scheduled events
    scheduled_events = reschedule_all_meetings(calender_events) 
    # Format the output
    output_formatted = format_to_output(scheduled_events, data, new_event)
    return output_formatted


@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    print(f"\n Received: {json.dumps(data, indent=2)}")
    new_data = your_meeting_assistant(data)
    print(f"\n\n\n Sending:\n {json.dumps(new_data, indent=2)}")
    return jsonify(new_data)

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    Thread(target=run_flask).start()