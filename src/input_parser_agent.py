from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
from pydantic_ai import Agent
import asyncio
from pydantic_ai.mcp import MCPServerStdio
from datetime import datetime, timedelta, time
from typing import Dict
from datetime import datetime
from pydantic_ai import Tool  
import nest_asyncio
from src.classes import Event
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import Literal

class MeetingSummary(BaseModel):
    START_TIME: str = Field(description="Meeting start time in YYYY-MM-DD HH:MM:SS format")
    END_TIME: str = Field(description="Meeting end time in YYYY-MM-DD HH:MM:SS format")
    SUMMARY: str = Field(description="Brief meeting summary")
    PRIORITY: Literal["1", "2", "3", "4"] = Field(description="Priority level 1-4")

# Set environment variables
os.environ["BASE_URL"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_KEY"] = "abc-123"

# Create OpenAI-compatible provider
provider = OpenAIProvider(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)

# Reference the model using the name from --served-model-name
agent_model = OpenAIModel("llama3-70b", provider=provider)

agent = Agent(
    model=agent_model
)

async def run_async(prompt: str) -> str:
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
        return result.output

    
@Tool
def calculate_meeting_times(ref_datetime_str: str, target_day: str) -> Dict[str, str]:
    """
    Given a reference starting datetime string, calculates the start and end datetime
    for a meeting on the next occurrence of a given day of the week.
    
    Args:
        ref_datetime_str: The starting datetime as a string in the format
                          "YYYY-MM-DD HH:MM:SS".
        target_day: The desired day of the week (e.g., "monday", "tuesday", etc.).
    
    Returns:
        A dictionary with "START_TIME" and "END_TIME" strings in YYYY-MM-DD HH:MM:SS format.
    
    Raises:
        ValueError: If an invalid target_day or datetime format is provided.
    """
    
    # # DEBUG: Print when tool is accessed
    # print("🔧 TOOL ACCESSED: YES")
    # print(f"🔧 TOOL INPUT - Reference datetime: {ref_datetime_str}")
    # print(f"🔧 TOOL INPUT - Target day: {target_day}")
    
    try:
        ref_datetime = datetime.strptime(ref_datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Invalid datetime format. Please use 'YYYY-MM-DD HH:MM:SS'.")
    
    days_of_week = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    target_day_lower = target_day.lower()
    if target_day_lower not in days_of_week:
        raise ValueError(f"Invalid target_day: '{target_day}'.")
    
    ref_day_num = ref_datetime.weekday()
    target_day_num = days_of_week[target_day_lower]
    days_to_add = (target_day_num - ref_day_num) % 7
    if days_to_add == 0:  # If it's the same day, get next week
        days_to_add = 7
    
    meeting_date = (ref_datetime + timedelta(days=days_to_add)).date()
    
    # Return with default 9 AM start, 1 hour duration
    start_time_str = f"{meeting_date} 09:00:00"
    end_time_str = f"{meeting_date} 10:00:00"
    
    result = {
        "START_TIME": start_time_str,
        "END_TIME": end_time_str
    }
    
    # # DEBUG: Print what tool returns
    # print(f"🔧 TOOL OUTPUT: {result}")
    # print(f"🔧 TOOL CALCULATION: {ref_datetime.strftime('%A %Y-%m-%d')} + {days_to_add} days = {meeting_date.strftime('%A %Y-%m-%d')}")
    
    return result

async def process_meeting_request(input_dict, agent_model):
    """Process meeting request and return parsed meeting details"""
    
    
    # Parse reference datetime
    try:
        reference_datetime = datetime.strptime(input_dict["Datetime"], "%d-%m-%YT%H:%M:%S")
    except ValueError:
        reference_datetime = datetime.fromisoformat(input_dict["Datetime"].replace('T', ' '))
    
    # Parse attendees
    attendees = []
    for attendee in input_dict["Attendees"]:
        attendees.append(attendee["email"])
    attendees.append(input_dict["From"])
    
    # Create agent with the tool
    agent = Agent(
        model=agent_model,
        output_type=MeetingSummary,
        tools=[calculate_meeting_times],  # Pass the tool here
        system_prompt = f"""You are an expert at parsing meeting requests and calculating dates relative to a reference point.

REFERENCE INFORMATION:
- Current datetime: {reference_datetime.strftime('%Y-%m-%d %H:%M:%S')}
- Current day: {reference_datetime.strftime('%A')}

CRITICAL TOOL USAGE RULES:
1. When the user mentions a weekday by NAME (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday):
   - YOU MUST use the calculate_meeting_times(ref_datetime_str, target_day) tool
   - The tool will return the CORRECT DATE - you MUST use this exact date
   - NEVER calculate the date yourself when a weekday name is mentioned
   - Only adjust the TIME portion based on user input (e.g., "4 pm" = 16:00:00)

2. DO NOT use the tool for: "tomorrow", "today", "next week", specific dates like "17th", "January 15th"

STEP-BY-STEP PROCESS FOR WEEKDAY NAMES:
1. Call the tool with the weekday name
2. Extract the DATE from tool's START_TIME (ignore the 09:00:00 time part)
3. Parse the user's requested time (e.g., "4 pm" = 16:00:00)
4. Combine: tool's DATE + user's TIME = final START_TIME
5. Add 1 hour for END_TIME (unless duration specified)

EXAMPLE:
- Tool returns: START_TIME: "2025-07-22 09:00:00" 
- User wants: "Tuesday at 4 pm"
- Your output: START_TIME: "2025-07-22 16:00:00", END_TIME: "2025-07-22 17:00:00"

DATE CALCULATION LOGIC FOR NON-WEEKDAYS:
- "today" = reference date
- "tomorrow" = reference date + 1 day  
- "next [day]" = first occurrence of that day after reference date
- Specific dates: Calculate directly (e.g., "17th" = 17th of current/next month)

TIME PARSING:
- Extract times: "3 pm" -> 15:00, "9:30 AM" -> 09:30
- Default time if none: 09:00
- Default duration: 1 hour
- Time windows: "morning" = 09:00, "afternoon" = 14:00, "evening" = 18:00

PRIORITY LEVELS:
1 = FIXED (unchangeable events like appointments, deadlines, client meetings)
2 = URGENT (time-sensitive but can be slightly adjusted if needed)
3 = IMPORTANT (significant events but with some scheduling flexibility)
4 = FLEXIBLE (can be easily rescheduled or moved)

VERIFICATION STEP:
Before providing your final answer, verify that if you used the tool, your START_TIME uses the same date as the tool's output if it was accessed


FINAL OUTPUT FORMAT:
START_TIME: YYYY-MM-DD HH:MM:SS
END_TIME: YYYY-MM-DD HH:MM:SS
SUMMARY: [Brief meeting summary]
PRIORITY: [1/2/3/4]

"""
    )
    
    # Create user prompt
    user_prompt = f"""MEETING REQUEST TO PARSE:
Subject: {input_dict["Subject"]}
Email Content: {input_dict["EmailContent"]}

Please parse this meeting request and provide the start time, end time, summary and priority."""
    
    # Run the agent
    result = await agent.run(user_prompt)
    return result.output




# write code to convert prioirity to a number

async def get_new_event(input_dict):
    summary = await process_meeting_request(input_dict, agent_model)
    attendees = []
    for attendee in input_dict["Attendees"]:
        attendees.append(attendee["email"])
    attendees.append(input_dict["From"])
    event = Event(
        creator=input_dict["From"],
        start_time=datetime.strptime(summary.START_TIME, "%Y-%m-%d %H:%M:%S"),
        end_time=datetime.strptime(summary.END_TIME, "%Y-%m-%d %H:%M:%S"),
        summary=summary.SUMMARY,
        attendees=attendees,
        priority=float(summary.PRIORITY) + 0.5
    )
    return event

import nest_asyncio
import asyncio

nest_asyncio.apply()
def get_new_event_sync(input_dict):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_new_event(input_dict))


