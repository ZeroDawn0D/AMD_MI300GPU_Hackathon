from src.calendar_events import get_all_calendar_events_dummy
from src.classes import Event
from src.scheduling.interval_tree import *

def test_tree_creation():
    calendar_events = get_all_calendar_events_dummy()
    scheduler = IntervalTreeScheduler(calendar_events)


def test_event_insertion_high_priority():
    calendar_events = get_all_calendar_events_dummy()
    scheduler = IntervalTreeScheduler(calendar_events)
    new_event = Event("usertwo.amd@gmail.com",
                      datetime(2025, 1, 2, 12, 0, 0),
                      datetime(2025, 1, 2, 13, 0, 0),
                      "Inserted Event",
                      ["userthree.amd@gmail.com", "usertwo.amd@gmail.com"],
                      priority=1)
    scheduler.insert_event(new_event)

def test_event_insertion_low_priority():
    calendar_events = get_all_calendar_events_dummy()
    scheduler = IntervalTreeScheduler(calendar_events)
    new_event = Event("usertwo.amd@gmail.com",
                      datetime(2025, 1, 2, 12, 0, 0),
                      datetime(2025, 1, 2, 13, 0, 0),
                      "Inserted Event",
                      ["userthree.amd@gmail.com", "usertwo.amd@gmail.com"],
                      priority=5)
    scheduler.insert_event(new_event)

if __name__ == "__main__":
    test_tree_creation()
    test_event_insertion_high_priority()
    test_event_insertion_low_priority()
    print("All scheduling tests passed.")