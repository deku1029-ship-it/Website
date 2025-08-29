# Cấu hình kết nối CSDL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ductinh1029@",
    database="task_db"
)
cursor = db.cursor()