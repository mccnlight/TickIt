from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite_utils import Database

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

conn = sqlite3.connect('tickit.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
''')

conn.commit()
conn.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/poster')
def poster():
    return render_template('poster.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/form')
def show_form():
    event_name = request.args.get('event', 'default_event')
    return render_template('form.html', default_event=event_name)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    event_name = request.form['event_name']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    phone_number = request.form['phone_number']

    # Connect to the SQLite database
    conn = sqlite3.connect('tickit.db')
    cursor = conn.cursor()

    # Check if the client already exists in the "clients" table
    cursor.execute('SELECT id FROM clients WHERE email = ?', (email,))
    client_id = cursor.fetchone()

    if client_id is None:
        # Check if email is unique
        cursor.execute('SELECT id FROM clients WHERE email = ?', (email,))
        existing_email = cursor.fetchone()

        # Check if phone number is unique
        cursor.execute('SELECT id FROM clients WHERE phone_number = ?', (phone_number,))
        existing_phone_number = cursor.fetchone()

        if existing_email or existing_phone_number:
            flash('Email or phone number already exists. Please use a unique email and phone number.')
            conn.close()
            return redirect(url_for('show_form'))


        # If the client does not exist, add them to the "clients" table
        cursor.execute('INSERT INTO clients (name, surname, email, phone_number) VALUES (?, ?, ?, ?)',
                       (name, surname, email, phone_number))
        conn.commit()

        # Retrieve the ID of the newly added client
        cursor.execute('SELECT id FROM clients WHERE email = ?', (email,))
        client_id = cursor.fetchone()[0]

    cursor.execute('SELECT price FROM events WHERE name = ?', (event_name,))
    event_price = cursor.fetchone()

    if event_price is None:
        return "Event not found in the database"

    # Extract the price value from the result
    price = float(event_price[0])

    # Retrieve the price of the event from the "events" table
    cursor.execute('SELECT id FROM events WHERE name = ? AND price = ?', (event_name, price))
    event_id_result = cursor.fetchone()

    print("event_id_result:", event_id_result)  # Debugging line

    if event_id_result is None:
        return "Event not found in the database"

    # Extract the event ID value from the result
    event_id = event_id_result[0]
    print("event_id:", event_id)  # Debugging line

    # Connect to the SQLite database
    db = Database("tickit.db")

    # Add the order to the "orders" table
    try:
        db["orders"].insert({"client_id": client_id, "event_id": event_id})
        return "Order submitted successfully!"
    except Exception as e:
        return f"Error submitting order: {str(e)}"

    return "Order submitted successfully!"

if __name__ == '__main__':
    app.run(debug=True)
