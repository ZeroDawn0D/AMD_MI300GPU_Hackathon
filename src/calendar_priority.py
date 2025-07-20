from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
from pydantic_ai import Agent
import asyncio

# Use the same environment variables and provider setup
os.environ["BASE_URL"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_KEY"] = "abc-123"

# Create OpenAI-compatible provider
provider = OpenAIProvider(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)

# Reference the same model as your existing agent
priority_agent_model = OpenAIModel("llama3-70b", provider=provider)

async def set_event_priorities(events: list) -> list:
    """
    Use LLM to analyze event summaries and set priority levels.
    Modifies the events in place and returns the updated list.
    
    Args:
        events: List of Event objects
        
    Returns:
        List of Event objects with updated priorities
    """
    
    # Extract summaries for LLM analysis
    summaries = []
    for i, event in enumerate(events):
        summaries.append(f"Event {i+1}: {event.summary}")
    summaries_text = "\n".join(summaries)
    
    # Create agent with priority classification system prompt
    priority_agent = Agent(
        model=priority_agent_model,
        system_prompt="""You are an expert at analyzing calendar events and assigning priority levels.

Based on the event summary, assign one of these priority levels:
1 = FIXED (unchangeable events like appointments, deadlines, client meetings)
2 = URGENT (time-sensitive but can be slightly adjusted if needed)
3 = IMPORTANT (significant events but with some scheduling flexibility like team meetings)
4 = FLEXIBLE (can be easily rescheduled or moved)

Consider factors like:
- Keywords indicating urgency (deadline, urgent, critical, emergency)
- Meeting types (client meetings, interviews = more fixed)
- Team activities (team meetings, discussions = more flexible)
- Personal vs professional context

Return ONLY the numbers (1, 2, 3, or 4) separated by commas, nothing else.
Example output: 2, 3, 1, 4"""
    )
    
    # Create user prompt
    user_prompt = f"""Analyze these event summaries and assign priority levels:
{summaries_text}

Return only the priority numbers separated by commas."""
    
    try:
        # Run the agent
        result = await priority_agent.run(user_prompt)
        content = result.output.strip()
        
        # Parse the comma-separated priorities
        priority_strings = content.split(',')
        priorities = [float(p.strip()) for p in priority_strings]
        
        # Update event objects with new priorities
        for i, event in enumerate(events):
            if i < len(priorities):
                event.priority = priorities[i]
            else:
                # Fallback if LLM didn't return enough priorities
                event.priority = 3.0  # Default to IMPORTANT
                
        return events
        
    except Exception as e:
        print(f"Error setting priorities: {e}")
        # Return events with default priorities unchanged
        return events

# Example usage function (similar to your existing pattern)
async def process_priority_request(events_list):
    """Process priority request and return updated events"""
    result = await set_event_priorities(events_list)
    return result

# If you need to run this synchronously, you can use:
def set_event_priorities_sync(events: list) -> list:
    """Synchronous wrapper for the async priority setting function"""
    return asyncio.run(set_event_priorities(events))