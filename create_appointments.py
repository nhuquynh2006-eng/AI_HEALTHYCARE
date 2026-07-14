"""Chạy 1 lần để tạo bảng appointments trong MySQL"""
import mysql.connector
conn = mysql.connector.connect(
    host="localhost", port=3310, user="root",
    password="Nhuquynh184@", database="healthcare_ai"
)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        user_id     INT NOT NULL,
        appt_date   DATE NOT NULL,
        note        TEXT,
        risk        FLOAT,
        created_at  DATETIME DEFAULT NOW()
    )
""")
conn.commit()
cursor.close()
conn.close()
print("✅ Tạo bảng appointments thành công!")