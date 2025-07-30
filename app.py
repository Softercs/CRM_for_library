from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("test.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['name']
        email = request.form['mail']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
        insert into user (name,password,admin,mail,is_issued) values (?, ?, false, ?, 0)
        """, (full_name, password, email))

        db.commit()
        db.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['mail']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE mail = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and user[2] == password:  # user[3] — это поле password в таблице
            if(user[3] == 1):
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))
        else:
            return "Неверный логин или пароль"

    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/user')
def user():
    return render_template("user.html")

@app.route('/readers')
def readers():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM user")
    readers = cur.fetchall()
    conn.close()

    # Простой текстовый вывод
    result = "<h1>Список читателей</h1><br>"

    for reader in readers:
        if reader['admin'] == 0:
            result += f"""
            ID: {reader['user_id']}<br>
            ФИО: {reader['name']}<br>
            Email: {reader['mail']}<br><br>
            """

    result += '<a href="/admin">← Назад</a>'
    return result

@app.route('/genres')
def genres():
    return render_template('genres.html')

@app.route('/genres/horror')
def genres_horror():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 1 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг жанра Хоррор</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/admin">← Назад</a>'
    return result
        
@app.route('/genres/fantasy')
def genres_fantasy():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 3 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг жанра Фантастики</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/admin">← Назад</a>'
    return result


@app.route('/genres/action')
def genres_action():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 2 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

   
    result = "<h1>Список книг жанра Боевик</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/admin">← Назад</a>'
    return result

@app.route('/books')
def books():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг:</h1><br>" 
    for book in books:
        result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """
    
    result += '<a href="/admin">← Назад</a>'
    return result

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        name = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        if genre == 'фантастика':
            genre = 3
        elif genre == 'боевик':
            genre = 2
        else:
            genre = 1
        
        conn = get_db()
        cur = conn.cursor()

        cur.execute("insert into books (Name, author, genre_id, is_deleted) values (?,?,?,false)", (name, author, genre))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    return render_template("add_book.html")

@app.route('/delete-book', methods=['GET', 'POST'])
def delete_book():
    if request.method == 'POST':
        name = request.form['title']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("select book_id, Name from books where is_deleted = 0")
        books = cur.fetchall()
        conn.close()
        flag = 0
        for book in books:
            if book[1] == name:
                flag = book[0]
                break
        if flag == 0:
            result = "<h3>Книга не найдена или уже удалена</h3><br>"
            result += '<a href="/admin">← Назад</a>'
            return result
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("update books set is_deleted = 1 where book_id = ?", (flag,))
        conn.commit()
        conn.close()
        result = "<h3>Книга успешно удалена</h3><br>"
        result += '<a href="/admin">← Назад</a>'
        return result

    return render_template("delete_books.html")

@app.route('/edit-book', methods=['GET', 'POST'])
def edit_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        name = request.form['title']
        author = request.form['author']
        genre = request.form ['genre']
        if genre == 'фантастика':
            genre = 3
        elif genre == 'боевик':
            genre = 2
        else:
            genre = 1

        conn = get_db()
        cur = conn.cursor()
        cur.execute("select Name, book_id from books where is_deleted = 0")
        books = cur.fetchall()
        conn.close()
        flag = 0
        for book in books:
            if book[1] is int(book_id):
                flag = book[1]
                break
        if flag == 0:
            result = "<h3>Книга не найдена или удалена</h3><br>"
            result += '<a href="/admin">← Назад</a>'
            return result
        conn = get_db()
        cur = conn.cursor()
        cur.execute("update books set Name = ?, author = ?, genre_id = ? where book_id = ?", (name, author, genre, flag))
        conn.commit()
        conn.close()

        result = "<h3>Книга отредоктирована</h3><br>"
        result += '<a href="/admin">← Назад</a>'
        return result

    return render_template("edit_book.html")

@app.route('/issue-book', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        mail = request.form['email']
        name = request.form['book_title']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("select Name from books where is_deleted = 0")
        books = cur.fetchall()
        conn.close()
        flag = 0
        for book in books:
            if book[0] == name:
                flag = 1
                break
        if flag == 0:
            result = "<h3>Книга не найдена или удалена</h3><br>"
            result += '<a href="/admin">← Назад</a>'
            return result

        conn = get_db()
        cur = conn.cursor()
        cur.execute("select user_id, mail from user where is_issued = 0")
        users = cur.fetchall()
        conn.close()

        flag = 0
        for user in users:
            if user[1] == mail:
                flag = user[0]
                break
        if flag == 0:
            result = "<h3>Пользователь не найден или не вернул прошлую книгу</h3><br>"
            result += '<a href="/admin">← Назад</a>'
            return result
        conn = get_db()
        cur = conn.cursor()
        cur.execute("update user set is_issued = true where user_id = ?", (flag,))
        conn.commit()
        conn.close()
        result = "<h3>Книга выдана</h3><br>"
        result += '<a href="/admin">← Назад</a>'
        return result

    return render_template('user_issued.html')

@app.route("/restore-book", methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        name = request.form['book_title']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("select Name, book_id from books where is_deleted = 1")
        books = cur.fetchall()
        conn.close()

        flag = 0
        for book in books:
            if book[0] == name:
                flag = book[1]
                break
        if flag == 0:
            result = "<h3>Книга не найдена или она не удалялась</h3><br>"
            result += '<a href="/admin">← Назад</a>'
            return result

        conn = get_db()
        cur = conn.cursor()
        cur.execute("update books set is_deleted = 0 where book_id = ?", (flag,))
        conn.commit()
        conn.close()
        result = "<h3>Книга успешно востановлена</h3><br>"
        result += '<a href="/admin">← Назад</a>'
        return result
        
    return render_template('return_book.html')


@app.route('/genres_user')
def genres_user():
    return render_template('genres_user.html')

@app.route('/genres/horror_user')
def genres_horror_user():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 1 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг жанра Хоррор</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/user">← Назад</a>'
    return result
        
@app.route('/genres/fantasy_user')
def genres_fantasy_user():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 3 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг жанра Фантастики</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/user">← Назад</a>'
    return result


@app.route('/genres/action_user')
def genres_action_user():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where genre_id = 2 and is_deleted = false")
    books = cur.fetchall()
    conn.close()

   
    result = "<h1>Список книг жанра Боевик</h1><br>"
    if not books:
        result += "<p>Нет книг в этом жанре.</p>"
    else:
        for book in books:
            result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """

    result += '<a href="/user">← Назад</a>'
    return result

@app.route('/books_user')
def books_user():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books where is_deleted = false")
    books = cur.fetchall()
    conn.close()

    result = "<h1>Список книг:</h1><br>" 
    for book in books:
        result += f"""
            ID: {book['book_id']}<br>
            Название: {book['Name']}<br>
            Автор: {book['author']}<br><br>
            """
    
    result += '<a href="/user">← Назад</a>'
    return result
