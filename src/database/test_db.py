from database.database import get_connection


conn1 = get_connection()
conn2 = get_connection()


print("Connection 1:", conn1)
print("Connection 2:", conn2)


if conn1 != conn2:
    print("SUCCESS: Separate connections created")
else:
    print("FAILED: Same connection")
    

conn1.close()
conn2.close()