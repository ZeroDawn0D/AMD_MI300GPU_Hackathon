# Smart Calendar Coordination System

## Overview

NOTE: This project is for team "Red Shirts" and is served on http://129.212.191.75

This project is developed for the AMD MI300GPU Hackathon. It's an intelligent calendar coordination system that automatically resolves scheduling conflicts across multiple users' calendars using AI-powered priority analysis and custom scheduling algorithms.

The system fetches calendar events from three users via Google Calendar API, analyzes event urgency using an LLM (Large Language Model), assigns priority scores, and uses a sophisticated interval tree-based scheduler to find optimal event arrangements that minimize conflicts.

<img width="1212" height="682" alt="image" src="https://github.com/user-attachments/assets/094590f0-4f8f-498e-bb12-8bf7bc660f26" />


## Features

- **Multi-User Calendar Integration**: Connects to Google Calendar API to fetch events from multiple users
- **AI-Powered Priority Analysis**: Uses LLM to analyze event summaries and assign priority scores (1-4 scale)
- **Intelligent Conflict Resolution**: Custom interval tree scheduler that resolves overlapping events based on priority
- **Real-time Processing**: Flask-based web service for handling scheduling requests
- **Flexible Rescheduling**: Finds nearest available time slots for conflicting events

## Novelty and Experiments

- The core scheduling logic is powered by a classic red-black tree modified to support interval scheduling specific to the problem statement. This code is under src/scheduling/
- We tried a variety of experiments and methodologies to maximise accuracy and minimise latency. In the limited time, we noticed that for the amount of reasoning we were asking the LLM to do, smaller models were incorrect half the time while larger models were exceeding the time limit of 10seconds. In the end, our final working snapshot was to use LLama 3.3 70B with one monolithic instruction
- Smaller models (LLaMA 8B, Deepseek 16B,  Qwen) were inaccurate half the time, these were giving us a sub 5second latency but unreliable
- LLaMA 3 70B follows instructions accurately and reasons well, but gives us a latency of around 11-16seconds

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── keys/                          # Google Calendar API tokens
│   ├── userone.amd.token
│   ├── usertwo.amd.token
│   └── userthree.amd.token
└── src/
    ├── __init__.py
    ├── main.py                    # Flask web service entry point
    ├── classes.py                 # Core Event class definition
    ├── calendar_events.py         # Google Calendar API integration
    ├── calendar_priority.py       # LLM-based priority assignment
    ├── output.py                  # Output formatting utilities
    ├── visualize.py              # Timeline visualization tools
    ├── tests.py                  # Basic interval tree tests
    └── scheduling/               # Core scheduling algorithms
        ├── __init__.py
        ├── interval_tree.py      # Red-Black tree based interval scheduler
        └── tests.py              # Scheduling algorithm tests
```

## Technical Approach

### 1. Data Collection
- **Google Calendar Integration**: Uses Google Calendar API to fetch events from three user accounts
- **Event Modeling**: Events are represented with creator, start/end times, summary, attendees, and priority
- **Authentication**: Secure OAuth2 token-based authentication for each user

### 2. Priority Analysis
- **LLM Integration**: Uses PydanticAI with OpenAI-compatible API to analyze event summaries
- **Priority Classification**: 4-tier priority system:
  - **1 = FIXED**: Unchangeable events (appointments, deadlines, client meetings)
  - **2 = URGENT**: Time-sensitive but slightly adjustable
  - **3 = IMPORTANT**: Significant events with scheduling flexibility
  - **4 = FLEXIBLE**: Easily rescheduled events
- **Context-Aware Analysis**: Considers keywords, meeting types, and professional vs personal context

### 3. Scheduling Algorithm
- **Interval Tree Data Structure**: Red-Black tree implementation for efficient interval operations
- **Conflict Detection**: O(log n) overlap detection using interval tree properties
- **Priority-Based Resolution**: Higher priority events retain their time slots
- **Optimal Rescheduling**: Finds nearest available slots for displaced events
- **Attendee Awareness**: Only considers conflicts when attendees overlap

### 4. Core Components

#### Event Class ([`src/classes.py`](src/classes.py))
- Represents calendar events with all necessary metadata
- Tracks original, window, and final scheduling times
- Supports priority assignment and attendee management

#### Calendar Integration ([`src/calendar_events.py`](src/calendar_events.py))
- **`get_all_calendar_events()`**: Fetches events from multiple users
- **`get_created_events()`**: Retrieves events for a specific user
- **`get_all_calendar_events_dummy()`**: Provides test cases for development

#### Priority Analysis ([`src/calendar_priority.py`](src/calendar_priority.py))
- **`set_event_priorities()`**: Async LLM-based priority assignment
- **`set_event_priorities_sync()`**: Synchronous wrapper for priority setting
- Uses structured prompts for consistent priority classification

#### Interval Tree Scheduler ([`src/scheduling/interval_tree.py`](src/scheduling/interval_tree.py))
- **`IntervalTree`**: Red-Black tree implementation with interval-specific operations
- **`IntervalTreeScheduler`**: High-level scheduling coordinator
- **`reschedule_all_meetings()`**: Main scheduling function
- Supports insertion, deletion, and conflict detection in O(log n) time

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AMD_MI300GPU_Hackathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Calendar API**
   - Create Google Cloud Project and enable Calendar API
   - Generate OAuth2 credentials for each user
   - Place token files in `keys/` directory

4. **Configure LLM Service**
   - Set up local LLM service on `http://localhost:8000/v1`
   - Or modify [`calendar_priority.py`](src/calendar_priority.py) for your LLM provider

## Usage

### Running the Web Service

```bash
python src/main.py
```

The service starts a Flask server on `http://0.0.0.0:5000` with the following endpoint:

- **POST `/receive`**: Accepts scheduling requests and returns coordinated calendar

### API Example

**Request Format:**
```json
{
  "Request_id": "12345",
  "Location": "Office",
  "From": "user@example.com",
  "Datetime": "2025-07-22T10:00:00+05:30",
  "Subject": "Team Meeting",
  "EmailContent": "Let's discuss project updates"
}
```

**Response Format:**
```json
{
  "Request_id": "12345",
  "EventStart": "2025-07-22T10:00:00+05:30",
  "EventEnd": "2025-07-22T10:30:00+05:30",
  "Duration_mins": 30,
  "Attendees": [
    {
      "email": "userone.amd@gmail.com",
      "events": [...]
    }
  ]
}
```

### Running Tests

```bash
# Test interval tree operations
python src/tests.py

# Test scheduling algorithms
python src/scheduling/tests.py
```

## Algorithm Complexity

- **Event Insertion**: O(log n) per event
- **Conflict Detection**: O(log n + k) where k is number of conflicts
- **Priority Sorting**: O(k log k) for k conflicting events
- **Rescheduling**: O(w/s) where w is search window and s is step size

## Key Innovations

1. **Attendee-Aware Conflicts**: Only reschedules when attendees actually overlap
2. **Priority-Driven Scheduling**: Higher priority events get preference for original time slots
3. **Efficient Data Structure**: Red-Black interval tree for optimal performance
4. **AI-Powered Priority**: Context-aware event importance analysis
5. **Flexible Rescheduling**: Bidirectional search for optimal alternative slots

## Dependencies

See [`requirements.txt`](requirements.txt) for complete list. Key dependencies:
- `google-api-python-client`: Google Calendar integration
- `pydantic-ai`: LLM integration for priority analysis
- `flask`: Web service framework
- `google-auth`: OAuth2 authentication
