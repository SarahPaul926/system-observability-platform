from database.database import get_connection
import time
def delete_OldData(days_to_Keep=7):
    conn=get_connection()
    cursor=conn.cursor()
    timeDelete=days_to_Keep * 24 * 60 * 60
    start=time.time()
    cursor.execute("""
        DELETE FROM telemetry
        where timeStamp < ?
        """,(time.time()-timeDelete,))
    deletedRows=cursor.rowcount
    total_time=time.time()-start
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "time_Deleted": timeDelete,
        "rows_delete": deletedRows,
        "execution_Time":total_time
    }