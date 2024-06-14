from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='chandu22',
        database='diary_app'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = create_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            connection.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = create_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect(url_for('entries'))
            else:
                return "Invalid credentials"
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html')

@app.route('/entries', methods=['GET', 'POST'])
def entries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form['content']
        user_id = session['user_id']
        
        connection = create_connection()
        cursor = connection.cursor()
        
        try:
            entry_date = date.today()
            cursor.execute("INSERT INTO diary_entries (user_id, entry_date, content) VALUES (%s, %s, %s)", 
                           (user_id, entry_date, content))
            connection.commit()
        finally:
            cursor.close()
            connection.close()
    
    user_id = session['user_id']
    connection = create_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT entry_date, content FROM diary_entries WHERE user_id = %s ORDER BY entry_date DESC", (user_id,))
        entries = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    
    return render_template('entries.html', entries=entries)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
