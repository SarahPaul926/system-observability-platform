import psutil
import time

def get_process():

    process = []
    for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    time.sleep(0.1)
    for p in psutil.process_iter():

        try:
            
            process.append({
                "process_id": p.pid,
                "name": p.name(),
                "cpu_percent": p.cpu_percent(None),
                "memory_percent": p.memory_percent()
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return process

## This give top 3 cpu and ram due to Sorting 
def correlate_cpu(processes,limit=3):
    processes_sorted = sorted( processes,
        key=lambda process: process["cpu_percent"],
        reverse=True
    )
    return processes_sorted[:limit]

def correlate_ram(processes, limit=3):
    processes_sorted = sorted(processes,
        key=lambda process: process["memory_percent"],
        reverse=True
    )
    return processes_sorted[:limit]

def correlate_processes(metric,issues,processes):
    correlations=[]
    resources=[issue["resource"] for issue in issues]
    if "CPU" in resources:
        top_cpu=correlate_cpu(processes)
        top_cpu = format_contributors(top_cpu)
        correlations.append({
            "resource":"CPU",
            "contributors":top_cpu
        })
    if "RAM" in resources:
        top_ram=correlate_ram(processes)
        top_ram = format_contributors(top_ram)
        correlations.append({
            "resource":"RAM",
            "contributors":top_ram
        })
    return correlations

## this basically makes it cleaner format
def format_contributors(process):
    contributors=[]
    for rank,process in enumerate(process,start=1):
        contributors.append({
            "rank":rank,
            "process_id":process["process_id"],
            "process":process["name"],
            "cpu":process["cpu_percent"],
            "memory":process["memory_percent"]
        })
    return contributors

def anomly_severity(anomaly,issues):
    if anomaly==-1 and len(issues)>=2:
        return "HIGH"
    if anomaly==-1:
        return "MEDIUM"
    return "LOW"

def format_processes(process):
    formatted=[]
    for p in process:
        formatted.append({
            "name":p["name"],
            "cpu":p["cpu_percent"],
            "memory":p["memory_percent"]
        })
    return formatted

def system_snapshot(metric,anomaly,issues,process):
    resources=[]
    for i in issues:
        resources.append(i["resource"])
    severity=anomly_severity(anomaly,issues)
    process_list=format_processes(process)
    return{
        "timestamp": metric["time"],
        "severity": severity,
        "anomaly": {
            "flag": anomaly,
            "resources": resources
        },
        "metrics": {
            "cpu": metric["cpu"]["cpu_usage"],
            "ram": metric["ram"]["percent"],
            "disk": metric["disk"]["disk_usage"],
            "network_sent": metric["network_activity"]["network_sent"],
            "network_received": metric["network_activity"]["network_received"]
        },
        "top_processes": process_list,
        "correlations": correlate_processes(metric,issues,process)
    }


if __name__ == "__main__":

    metric = {
        "time": 1787661473,

        "cpu": {
            "cpu_usage": 93.2
        },

        "ram": {
            "percent": 54.2
        },

        "disk": {
            "disk_usage": 94.1
        },

        "network_activity": {
            "network_sent": 0.02,
            "network_received": 0.01
        }
    }

    issues = [
        {
            "resource": "CPU",
            "message": "CPU usage is critically high: 93.2%"
        },
        {
            "resource": "DISK",
            "message": "Disk usage is critically high: 94.1%"
        }
    ]

    processes = [
        {
            "process_id": 1234,
            "name": "WhatsApp.exe",
            "cpu_percent": 51.2,
            "memory_percent": 8.2
        }
    ]

    incident = system_snapshot(
        metric,
        -1,
        issues,
        processes
    )

    print(incident)

