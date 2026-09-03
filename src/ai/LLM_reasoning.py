import os
import json
from dotenv import load_dotenv
from google import genai
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Warning: API_KEY not found in .env")
    client = None

else:
    client = genai.Client(
        api_key=API_KEY
    )

SYSTEM_PROMPT = """
You are Helios, an AI system diagnostics assistant.

Your task is to analyze system telemetry and incident
information provided in the user input.

STRICT RULES:

1. Use ONLY the information provided in the telemetry JSON.
2. Do not invent processes, applications, metrics, events,
   or causes.
3. Observed processes are contributors, not definitive causes.
4. Do not claim certainty when the evidence is insufficient.
5. If the root cause cannot be determined, explicitly say so.
6. Recommendations must be practical, actionable, and directly
   connected to the observed telemetry.
7. Each recommendation must explain WHY it is being suggested.
8. Do not recommend actions based on assumptions about what a
   process is doing internally.
9. If the evidence is insufficient to provide a specific
   recommendation, recommend collecting more telemetry instead.

Return ONLY valid JSON.

The JSON must contain:

{
    "summary": "...",
    "root_cause": "...",
    "contributors": [],
    "recommendations": [],
    "confidence": 0.0
}
"""

def analyze_incident(incident):
    incident_json=json.dumps(incident,indent=2)
    prompt=f""" Analyze this Helios incident: {incident_json}"""
    try:
        response = client.interactions.create(
            model="gemini-3.6-flash",
            system_instruction=SYSTEM_PROMPT,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "root_cause": {"type": "string"},
                        "contributors": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "confidence": {"type": "number"}
                    },
                    "required": [
                        "summary",
                        "root_cause",
                        "contributors",
                        "recommendations",
                        "confidence"
                    ]
                }
            }
        )
        if response.output_text:
            return json.loads(response.output_text)

        else:
            return {
                "summary": "AI assistance unavailable.",
                "root_cause": "Unable to analyze incident.",
                "contributors": [],
                "recommendations": [],
                "confidence": 0.0
            }
    except Exception as e:
        print( f"Gemini API error: {e}")
        return {
            "summary": "AI assistance unavailable.",
            "root_cause": "Unable to analyze incident.",
            "contributors": [],
            "recommendations": [],
            "confidence": 0.0
        }
    
if __name__ == "__main__":

    incident = {
        "metrics": {
            "cpu": 93.2,
            "ram": 54.2,
            "disk": 94.1,
            "network_sent": 0.02,
            "network_received": 0.01
        },

        "issues": [
            {
                "resource": "CPU",
                "message": "CPU usage is critically high: 93.2%"
            },
            {
                "resource": "DISK",
                "message": "Disk usage is critically high: 94.1%"
            }
        ],

        "top_processes": [
            {
                "name": "WhatsApp.exe",
                "cpu": 51.2,
                "memory": 8.2
            },
            {
                "name": "chrome.exe",
                "cpu": 20.1,
                "memory": 14.5
            }
        ]
    }

    result = analyze_incident(incident)

    print(json.dumps(result, indent=4))
