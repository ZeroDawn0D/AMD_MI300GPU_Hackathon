from classes import Event
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from pathlib import Path

KEYS_PATH = Path("./keys")

def get_all_calendar_events(users: list[str], start_date: str, end_date: str) -> list[Event]:
    events_list = []
    for user in users:
        events_list.extend(get_created_events(user, start_date, end_date))
    return events_list


def get_created_events(user: str, start: str, end: str) -> list[Event]:

    events_list = []
    token_path = KEYS_PATH / (user.split("@")[0]+".token")
    user_creds = Credentials.from_authorized_user_file(token_path)
    calendar_service = build("calendar", "v3", credentials=user_creds)
    events_result = calendar_service.events().list(calendarId='primary', timeMin=start,timeMax=end,singleEvents=True,orderBy='startTime').execute()
    events = events_result.get('items')
    
    for event in events : 
        # creator
        creator = event["creator"]["email"]
        if creator != user:
            continue

        # attendees
        attendee_list = []
        try:
            for attendee in event["attendees"]: 
                attendee_list.append(attendee['email'])
        except: 
            attendee_list.append("SELF")

        # start and end time
        time_field = "dateTime" if "dateTime" in event["start"] else "date"
        start_time = datetime.fromisoformat(event["start"][time_field])
        end_time = datetime.fromisoformat(event["end"][time_field])

        # summary
        summary = event["summary"]

        event_obj = Event(creator, start_time, end_time, summary, attendee_list)
        events_list.append(event_obj)

    return events_list

def get_all_calendar_events_dummy() -> list[Event]:
    # Dummy data for testing purposes
    return [
        Event("userone.amd@gmail.com", datetime(2025, 1, 1, 10, 0, 0), 
              datetime(2025, 1, 1, 11, 0, 0), "Meeting with team", [
                  "usertwo.amd@gmail.com", "userthree.amd@gmail.com", "userone.amd@gmail.com"
            ]),
        Event("usertwo.amd@gmail.com", datetime(2025, 1, 2, 12, 0, 0),
                datetime(2025, 1, 2, 13, 0, 0), "Project discussion", [
                    "userthree.amd@gmail.com", "usertwo.amd@gmail.com"
            ]),
        Event("usertwo.amd@gmail.com", datetime(2025, 1, 2, 12, 30, 0),
                datetime(2025, 1, 2, 13, 30, 0), "Tea break", [
                    "userone.amd@gmail.com", "usertwo.amd@gmail.com"
            ]) 
    ]