from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('url_database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            original_url TEXT NOT NULL,
            short_url TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_url(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url()

        conn = sqlite3.connect('url_database.db')
        c = conn.cursor()

        # Ensure unique short_url
        while True:
            c.execute("SELECT * FROM urls WHERE short_url=?", (short_url,))
            if not c.fetchone():
                break
            short_url = generate_short_url()

        c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()
        conn.close()

        short_url = request.host_url + short_url

    return render_template('index.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = sqlite3.connect('url_database.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "<h1>URL not found</h1>", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
