import sqlite3

conn = sqlite3.connect("server.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS servers (ip INT, password VARCHAR(255) NOT NULL)""")

cursor.execute("""INSERT INTO server (ip, password) VALUES
('192.168.1.13', 'qfewgvaetbh'), 
('192.168.11.1', '123123123123')
""")

conn.commit()

cursor.execute("SELECT password FROM server WHERE ip='192.168.11.1'")
rows = cursor.fetchall()

for row in rows:
    print(row)
