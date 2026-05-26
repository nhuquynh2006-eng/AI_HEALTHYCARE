import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3310,
    user="root",
    password="Nhuquynh184@",
    database="healthcare_ai"
)

cursor = conn.cursor()