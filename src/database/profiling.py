from database.database import get_connection
import time
def profiling_Time():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        SELECT * FROM telemetry
        where timeStamp > ?
        """,(time.time()-100,))
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return {
        "query_time": len(result),
        "rows_found": len(result)
    }

    