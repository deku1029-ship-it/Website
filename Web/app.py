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

    query = "SELECT * FROM tasks WHERE user_id = %s"
    params = [session['user_id']]

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
        "INSERT INTO tasks (title, description, due_date, label, category, status, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title, description, due_date, label, category, status, session['user_id'])
    )
    db.commit()
    return redirect('/')

# SỬA CÔNG VIỆC
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor_dict = db.cursor(dictionary=True)
    cursor_dict.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (id, session['user_id']))
    task = cursor_dict.fetchone()

    if not task:
        return "Không tìm thấy công việc hoặc bạn không có quyền chỉnh sửa", 404

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        label = request.form['label']
        category = request.form['category']
        status = request.form.get('status', 'Chưa hoàn thành')

        cursor.execute(
            "UPDATE tasks SET title = %s, description = %s, due_date = %s, label = %s, category = %s, status = %s WHERE id = %s AND user_id = %s",
            (title, description, due_date, label, category, status, id, session['user_id'])
        )
        db.commit()
        return redirect('/')
    else:
        return render_template('edit_task.html', task=task)

# XÓA CÔNG VIỆC
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (id, session['user_id']))
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
        cursor_dict = db.cursor(dictionary=True)
        cursor_dict.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor_dict.fetchone()
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
