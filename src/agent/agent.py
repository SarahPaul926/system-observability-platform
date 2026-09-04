from core.Telemetry.engine import TelemetryEngine
import time
import requests
API_URL = "https://helios-observability.onrender.com/api/metrics/telemetry"
def run_agent():
    while True:
        telemetry=TelemetryEngine.capture_frame()
        print("Collected telemetry:")
        print(telemetry)
        try:
            response=requests.post(API_URL,json=telemetry,timeout=30)
            print("Status code:", response.status_code)
            print("Server response:", response.text)
        except requests.exceptions.RequestException as e:
            print("Could not send teh telmentry engine data ",e)
        time.sleep(2)

if __name__=="__main__":
    run_agent()