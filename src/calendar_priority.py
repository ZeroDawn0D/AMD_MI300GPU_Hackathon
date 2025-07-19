import requests

def set_event_priorities(events: list, url: str = "http://localhost:4000/v1/chat/completions") -> list:
    """
    Use LLM to analyze event summaries and set priority levels.
    Modifies the events in place and returns the updated list.
    
    Args:
        events: List of Event objects
        url: vLLM API endpoint URL
    
    Returns:
        List of Event objects with updated priorities
    """
    
    # Extract summaries for LLM analysis
    summaries = []
    for i, event in enumerate(events):
        summaries.append(f"Event {i+1}: {event.summary}")
    
    summaries_text = "\n".join(summaries)
    
    # System prompt for priority classification
    system_prompt = """You are an expert at analyzing calendar events and assigning priority levels.

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

    user_prompt = f"""Analyze these event summaries and assign priority levels:

{summaries_text}

Return only the priority numbers separated by commas."""

    # API request
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "/home/user/Models/meta-llama/Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "stream": False,
        "max_tokens": 100,
        "temperature": 0  # Lower temperature for more consistent classification
    }
    
    try:
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Extract priorities from response
        response_json = response.json()
        content = response_json['choices'][0]['message']['content'].strip()
        
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


