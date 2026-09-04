from core.Telemetry.engine import TelemetryEngine
import time
import requests
API_URL = "https://helios-observability.onrender.com/api/metrics/telemetry"
while True:
    telemetry=TelemetryEngine.capture_frame()
    print("Collected telemetry:")
    print(telemetry)
    try:
        response=requests.post(API_URL,json=telemetry)
        print("Status code:", response.status_code)
        print("Server response:", response.text)
    except requests.exceptions.RequestException as e:
        print("Could not send teh telmentry engine data ",e)
    time.sleep(2)