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

def test_1():
    calendar_events = get_all_calendar_events_dummy(1)
    scheduler = IntervalTreeScheduler(calendar_events)
    
    """new_event =Event("userthree.amd@gmail.com",
                     datetime(2025, 1, 2, 11, 0, 0),
                     datetime(2025, 1, 2, 13, 0, 0),
                     "Tea break", ["usertwo.amd@gmail.com", "userthree.amd@gmail.com"],
                     priority=4)
    scheduler.insert_event(new_event)"""
    print(scheduler)

def test_2():
    calendar_events = get_all_calendar_events_dummy(2)
    scheduler = IntervalTreeScheduler(calendar_events)
    
    """new_event = Event("userthree.amd@gmail.com",
                      datetime(2025, 1, 1, 13, 0, 0),
                      datetime(2025, 1, 1, 13, 30, 0),
                      "Joining celebrations for new employees",
                      ["userthree.amd@gmail.com", "userone.amd@gmail.com"],
                      priority=4)
    scheduler.insert_event(new_event)"""
    print(scheduler)

def test_3():
    calendar_events = get_all_calendar_events_dummy(3)
    scheduler = IntervalTreeScheduler(calendar_events)
    
    """new_event = Event("userthree.amd@gmail.com",
                      datetime(2025, 1, 1, 13, 0, 0),
                      datetime(2025, 1, 1, 14, 0, 0), 
                      "Joining celebrations for new employees", 
                      ["userthree.amd@gmail.com", "userone.amd@gmail.com"],
                      priority=4)
    scheduler.insert_event(new_event)"""
    print(scheduler)

def test_4():
    calendar_events = get_all_calendar_events_dummy(4)
    scheduler = IntervalTreeScheduler(calendar_events)
    
    """new_event = Event("userthree.amd@gmail.com",
                      datetime(2025, 1, 1, 13, 0, 0),
                      datetime(2025, 1, 1, 14, 0, 0), 
                      "Joining celebrations for new employees", 
                      ["userthree.amd@gmail.com", "userone.amd@gmail.com"],
                      priority=4)
    scheduler.insert_event(new_event)"""
    print(scheduler)

if __name__ == "__main__":
    #test_tree_creation()
    #test_event_insertion_high_priority()
    #test_event_insertion_low_priority()
    #test_1()
    #test_2()
    #test_3()
    test_4()
    print("All scheduling tests passed.")