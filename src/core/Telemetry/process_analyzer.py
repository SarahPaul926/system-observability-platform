import psutil
def get_process():
    process=[]
    for p in psutil.process_iter():
        try:
            process.append({
                "process_id":p.pid,
                "name":p.name(),
                "cpu_percent":p.cpu_percent(interval=0.1),
                "memory_percent":p.memory_percent()
            })
        except(psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return process

def get_cpu_percent(limit=5):
    process_list=get_process()
    process_list.sort(key=lambda process_list:process_list["cpu_percent"],reverse=True)
    return process_list[:limit]

def get_ram_percent(limit=5):
    process_list=get_process()
    process_list.sort(key=lambda process_list:process_list["memory_percent"],reverse=True)
    return process_list[:limit]

