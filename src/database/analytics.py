# This Handles the calculations , reports and statistics
import sqlite3 as sq
def system_analysis():
    conn=sq.connect("telemetry_history.db")
    cursor=conn.cursor()
    cursor.execute(""" 
               SELECT AVG(cpu_usage),
               MAX(ram_usage) from telemetry
    """)
    result=cursor.fetchone()
    avg_cpu,max_ram=  result[0],result[1]
    cursor.close()
    conn.close()
    return {"average_cpu":avg_cpu,"maximum_ram":max_ram}

