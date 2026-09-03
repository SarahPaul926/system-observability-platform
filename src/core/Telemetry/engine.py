import psutil
import time

class TelemetryEngine:
    previous_sent=0
    previous_received=0
    @staticmethod
    def capture_frame():
        # CPU intake
        cpu_usage=psutil.cpu_percent(interval=0.1)
        cpu_freq=psutil.cpu_freq().current
        cpu_stats=psutil.cpu_stats()._asdict()
        cpu_time=psutil.cpu_times()._asdict()

        # Memory & RAM intake
        memory=psutil.virtual_memory()
        ram_total=memory.total
        ram_available=memory.available
        ram_percent=memory.percent
        memory_swap=psutil.swap_memory().percent

        # DISK LAYER intake
        read_bytes=psutil.disk_io_counters().read_bytes # calaculate throughput
        write_bytes=psutil.disk_io_counters().write_bytes
        disk_usage=psutil.disk_usage('/').percent

        # Network Layer & Process 
        network=psutil.net_io_counters()
        current_sent=network.bytes_sent
        current_received=network.bytes_recv
        network_sent=current_sent-TelemetryEngine.previous_sent
        network_received=current_received-TelemetryEngine.previous_received
        TelemetryEngine.previous_sent=current_sent
        TelemetryEngine.previous_received=current_received

        telemetry={
            "time":time.time(),
            "cpu":{
                "cpu_usage":cpu_usage,
                "cpu_freq":cpu_freq,
                "cpu_switch":cpu_stats,
                "cpu_time":cpu_time,

            },
            "ram":{
                "total":ram_total,
                "available":ram_available,
                "percent":ram_percent,
                "memory_swap":memory_swap,   
            },
            "disk":{
                "read_bytes":read_bytes,
                "write_bytes":write_bytes,
                "disk_usage":disk_usage,
            },
            "network_activity":{
                "network_sent":round(network_sent/(1024*1024),2),
                "network_received":round(network_received/(1024*1024),2)
            },
            
        }

        return telemetry
