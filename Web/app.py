from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "Ductinh1029@"  # Khóa bảo mật cho session

# Cấu hình kết nối CSDL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ductinh1029@",
    database="task_db"
)
cursor = db.cursor()

# TRANG CHÍNH: Lọc theo ngày, trạng thái, tìm kiếm
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    date_filter = request.args.get('date_filter')
    search = request.args.get('search')
    status_filter = request.args.get('status_filter')

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if date_filter:
        query += " AND due_date = %s"
        params.append(date_filter)

    if search:
        query += " AND (title LIKE %s OR description LIKE %s)"
        keyword = f"%{search}%"
        params.extend([keyword, keyword])

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    cursor.execute(query, tuple(params))
    tasks = cursor.fetchall()

    return render_template('index.html', tasks=tasks)

# THÊM CÔNG VIỆC
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    due_date = request.form['due_date']
    label = request.form['label']
    category = request.form['category']
    status = request.form.get('status', 'Chưa hoàn thành')

    cursor.execute(
        "INSERT INTO tasks (title, description, due_date, label, category, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (title, description, due_date, label, category, status)
    )
    db.commit()
    return redirect('/')

# SỬA CÔNG VIỆC — Đã sửa lỗi ở đây
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        label = request.form['label']
        category = request.form['category']
        status = request.form.get('status', 'Chưa hoàn thành')  # Sửa ở đây

        cursor.execute(
            "UPDATE tasks SET title = %s, description = %s, due_date = %s, label = %s, category = %s, status = %s WHERE id = %s",
            (title, description, due_date, label, category, status, id)
        )
        db.commit()
        return redirect('/')
    else:
        cursor_dict = db.cursor(dictionary=True)
        cursor_dict.execute("SELECT * FROM tasks WHERE id = %s", (id,))
        task = cursor_dict.fetchone()
        if task:
            return render_template('edit_task.html', task=task)
        else:
            return "Không tìm thấy công việc", 404

# XÓA CÔNG VIỆC
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
    db.commit()
    return redirect('/')

# ĐĂNG KÝ
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            return redirect("/login")
        except:
            flash("Tên đăng nhập đã tồn tại.")
            return redirect("/register")
    return render_template("register.html")

# ĐĂNG NHẬP
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        else:
            flash("Sai thông tin đăng nhập.")
            return redirect("/login")
    return render_template("login.html")

# ĐĂNG XUẤT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)