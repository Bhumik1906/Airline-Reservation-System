"""
SkyBook Airlines - Airline Reservation System
A simple, beginner-friendly Flask web application for a college Software Engineering mini-project.
"""

import os
import sqlite3
import random
import string
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, 
    url_for, session, flash, g, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)
# Secret key for session management and flash messages
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'skybook_secure_college_project_key_2026')

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================

def get_db():
    """
    Connects to the SQLite database.
    row_factory is set to sqlite3.Row to access columns by name like a dictionary.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        # Enable foreign key support in SQLite
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Closes the database connection when the request finishes."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Initializes the database tables and populates sample data
    for users, flights, and bookings if not already present.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Flights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT UNIQUE NOT NULL,
            airline TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            duration TEXT NOT NULL,
            total_seats INTEGER NOT NULL DEFAULT 60,
            available_seats INTEGER NOT NULL DEFAULT 60,
            price REAL NOT NULL
        )
    ''')

    # 3. Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_reference TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            passenger_name TEXT NOT NULL,
            passenger_age INTEGER NOT NULL,
            passenger_gender TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            seat_number TEXT NOT NULL,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Confirmed',
            total_fare REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (flight_id) REFERENCES flights (id) ON DELETE RESTRICT
        )
    ''')
    conn.commit()

    # 4. Seed default Admin and Demo User if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash("admin123")
        user_pass = generate_password_hash("user123")
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("System Admin", "admin@skybook.com", admin_pass, "9876543210", "admin"))

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("Rahul Sharma", "rahul@gmail.com", user_pass, "9812345678", "user"))
        conn.commit()

    # 5. Seed sample flights across major Indian cities if empty
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] == 0:
        today = date.today()
        
        # Flight route templates
        route_templates = [
            ("SkyBook Express", "Ahmedabad", "Mumbai", "06:30 AM", "07:45 AM", "1h 15m", 3200),
            ("Air India", "Ahmedabad", "Delhi", "08:15 AM", "09:50 AM", "1h 35m", 4100),
            ("IndiGo", "Mumbai", "Delhi", "09:00 AM", "11:15 AM", "2h 15m", 4800),
            ("SkyBook Express", "Delhi", "Bengaluru", "10:30 AM", "01:15 PM", "2h 45m", 5900),
            ("SpiceJet", "Bengaluru", "Chennai", "07:00 AM", "08:00 AM", "1h 00m", 2500),
            ("IndiGo", "Mumbai", "Goa", "11:45 AM", "12:55 PM", "1h 10m", 2900),
            ("SkyBook Express", "Ahmedabad", "Bengaluru", "02:00 PM", "04:10 PM", "2h 10m", 5200),
            ("Air India", "Delhi", "Mumbai", "04:30 PM", "06:45 PM", "2h 15m", 4950),
            ("IndiGo", "Chennai", "Delhi", "01:20 PM", "04:10 PM", "2h 50m", 5600),
            ("SkyBook Express", "Mumbai", "Ahmedabad", "07:30 PM", "08:45 PM", "1h 15m", 3100),
            ("Air India", "Delhi", "Ahmedabad", "06:00 PM", "07:35 PM", "1h 35m", 4250),
            ("IndiGo", "Bengaluru", "Delhi", "05:15 PM", "08:00 PM", "2h 45m", 5750),
            ("SkyBook Express", "Chennai", "Bengaluru", "09:30 PM", "10:30 PM", "1h 00m", 2400),
            ("SpiceJet", "Ahmedabad", "Goa", "03:15 PM", "04:55 PM", "1h 40m", 3800),
        ]

        flight_id_counter = 101
        # Populate flights across today and the next 10 days
        for day_offset in range(10):
            current_date_str = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            for airline, src, dest, dep, arr, dur, price in route_templates:
                flight_no = f"SB-{flight_id_counter}"
                # Small price variation for different days
                daily_price = price + (day_offset * 50)
                cursor.execute('''
                    INSERT INTO flights (
                        flight_number, airline, source, destination, 
                        departure_time, arrival_time, flight_date, 
                        duration, total_seats, available_seats, price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 60, 60, ?)
                ''', (flight_no, airline, src, dest, dep, arr, current_date_str, dur, daily_price))
                flight_id_counter += 1

        conn.commit()

        # 6. Seed sample bookings for the demo user
        # Get demo user id and a flight id
        cursor.execute("SELECT id FROM users WHERE email = 'rahul@gmail.com'")
        user_row = cursor.fetchone()
        cursor.execute("SELECT id, price FROM flights LIMIT 2")
        flight_rows = cursor.fetchall()

        if user_row and len(flight_rows) >= 2:
            uid = user_row[0]
            # Booking 1: Confirmed
            cursor.execute('''
                INSERT INTO bookings (
                    booking_reference, user_id, flight_id, passenger_name, 
                    passenger_age, passenger_gender, contact_number, 
                    seat_number, status, total_fare
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
            ''', ("SB-78192", uid, flight_rows[0][0], "Rahul Sharma", 24, "Male", "9812345678", "3A", flight_rows[0][1]))
            # Deduct seat
            cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = ?", (flight_rows[0][0],))

            # Booking 2: Confirmed
            cursor.execute('''
                INSERT INTO bookings (
                    booking_reference, user_id, flight_id, passenger_name, 
                    passenger_age, passenger_gender, contact_number, 
                    seat_number, status, total_fare
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
            ''', ("SB-49210", uid, flight_rows[1][0], "Priya Sharma", 22, "Female", "9812345678", "3B", flight_rows[1][1]))
            # Deduct seat
            cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = ?", (flight_rows[1][0],))
            conn.commit()

    conn.close()


# ==========================================
# AUTHENTICATION DECORATORS
# ==========================================

def login_required(f):
    """Ensures user is logged in before accessing protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first to continue.", "warning")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Ensures logged-in user has admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Admin login required.", "warning")
            return redirect(url_for('login', next=request.path))
        if session.get('user_role') != 'admin':
            flash("Access denied: Admin privileges required.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def generate_pnr():
    """Generates a unique 6-character booking reference code (e.g., SB-8392)."""
    digits = ''.join(random.choices(string.digits, k=5))
    return f"SB-{digits}"


def get_all_cities():
    """Retrieves unique city names from the flights database for search dropdowns."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT DISTINCT source AS city FROM flights 
        UNION 
        SELECT DISTINCT destination AS city FROM flights 
        ORDER BY city ASC
    ''')
    rows = cursor.fetchall()
    return [row['city'] for row in rows]


# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.route('/')
def index():
    """Homepage: Flight search bar, popular routes, and company highlights."""
    cities = get_all_cities()
    today_str = date.today().strftime("%Y-%m-%d")

    # Fetch 4 featured upcoming flights
    db = get_db()
    featured_flights = db.execute('''
        SELECT * FROM flights 
        WHERE flight_date >= ? AND available_seats > 0
        ORDER BY flight_date ASC, price ASC 
        LIMIT 4
    ''', (today_str,)).fetchall()

    return render_template(
        'index.html', 
        cities=cities, 
        today=today_str, 
        featured_flights=featured_flights
    )


@app.route('/flights')
def flights():
    """
    Search Flights page:
    Filters flights based on source, destination, and travel date.
    If no filters given, lists upcoming flights.
    """
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    flight_date = request.args.get('date', '').strip()
    sort_by = request.args.get('sort', 'price_asc')

    cities = get_all_cities()
    db = get_db()

    query = "SELECT * FROM flights WHERE 1=1"
    params = []

    if source:
        query += " AND LOWER(source) = LOWER(?)"
        params.append(source)
    if destination:
        query += " AND LOWER(destination) = LOWER(?)"
        params.append(destination)
    if flight_date:
        query += " AND flight_date = ?"
        params.append(flight_date)
    else:
        # Default: show today onwards
        today_str = date.today().strftime("%Y-%m-%d")
        query += " AND flight_date >= ?"
        params.append(today_str)

    # Sorting
    if sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'date_asc':
        query += " ORDER BY flight_date ASC, departure_time ASC"
    else:
        query += " ORDER BY price ASC"

    available_flights = db.execute(query, params).fetchall()

    return render_template(
        'flights.html',
        flights=available_flights,
        cities=cities,
        selected_source=source,
        selected_destination=destination,
        selected_date=flight_date,
        selected_sort=sort_by
    )


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user account registration."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic form validations
        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('register.html', name=name, email=email, phone=phone)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', name=name, email=email, phone=phone)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email, phone=phone)

        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        # Secure password hashing using Werkzeug
        password_hash = generate_password_hash(password)

        db.execute('''
            INSERT INTO users (name, email, password_hash, phone, role)
            VALUES (?, ?, ?, ?, 'user')
        ''', (name, email, password_hash, phone))
        db.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user and administrator login."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_page = request.form.get('next') or url_for('index')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', next=next_page)

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            # Store user details in session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash(f"Welcome back, {user['name']}!", "success")

            # If admin, redirect to admin dashboard; else redirect to next_page or home
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(next_page if next_page.startswith('/') else url_for('index'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html', next=next_page)


@app.route('/logout')
def logout():
    """Clears user session and logs out."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('index'))


# ==========================================
# BOOKING ROUTES
# ==========================================

@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def book_flight(flight_id):
    """
    Flight Booking page:
    - Displays flight information.
    - Shows interactive airplane seat map (Rows 1-10, A-F).
    - Checks already occupied seats.
    - Captures passenger details and confirms booking.
    """
    db = get_db()
    flight = db.execute("SELECT * FROM flights WHERE id = ?", (flight_id,)).fetchone()

    if not flight:
        flash("Flight not found.", "danger")
        return redirect(url_for('flights'))

    if flight['available_seats'] <= 0:
        flash("Sorry, this flight is fully booked.", "warning")
        return redirect(url_for('flights'))

    # Fetch currently booked/confirmed seats for this flight
    booked_rows = db.execute('''
        SELECT seat_number FROM bookings 
        WHERE flight_id = ? AND status = 'Confirmed'
    ''', (flight_id,)).fetchall()
    booked_seats = [row['seat_number'].strip().upper() for row in booked_rows]

    # Generate standard seat layout: 10 rows, columns A, B, C (aisle) D, E, F
    seat_columns = ['A', 'B', 'C', 'D', 'E', 'F']
    total_rows = 10
    seat_layout = []
    for r in range(1, total_rows + 1):
        row_seats = []
        for c in seat_columns:
            seat_code = f"{r}{c}"
            row_seats.append({
                'code': seat_code,
                'is_booked': seat_code in booked_seats
            })
        seat_layout.append(row_seats)

    if request.method == 'POST':
        passenger_name = request.form.get('passenger_name', '').strip()
        passenger_age = request.form.get('passenger_age', '').strip()
        passenger_gender = request.form.get('passenger_gender', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        selected_seat = request.form.get('seat_number', '').strip().upper()

        # Validation
        if not passenger_name or not passenger_age or not passenger_gender or not contact_number or not selected_seat:
            flash("All passenger and seat details are required.", "danger")
            return render_template('booking.html', flight=flight, seat_layout=seat_layout, booked_seats=booked_seats)

        try:
            passenger_age = int(passenger_age)
            if passenger_age < 1 or passenger_age > 120:
                flash("Please enter a valid passenger age.", "danger")
                return render_template('booking.html', flight=flight, seat_layout=seat_layout, booked_seats=booked_seats)
        except ValueError:
            flash("Age must be a valid number.", "danger")
            return render_template('booking.html', flight=flight, seat_layout=seat_layout, booked_seats=booked_seats)

        # Seat availability check: Prevent double booking of the exact same seat
        seat_conflict = db.execute('''
            SELECT id FROM bookings 
            WHERE flight_id = ? AND seat_number = ? AND status = 'Confirmed'
        ''', (flight_id, selected_seat)).fetchone()

        if seat_conflict:
            flash(f"Seat {selected_seat} is already booked! Please select a different seat.", "danger")
            return render_template('booking.html', flight=flight, seat_layout=seat_layout, booked_seats=booked_seats)

        # Generate unique PNR reference
        pnr = generate_pnr()
        # Verify PNR uniqueness
        while db.execute("SELECT id FROM bookings WHERE booking_reference = ?", (pnr,)).fetchone():
            pnr = generate_pnr()

        total_fare = float(flight['price'])

        # Save booking in database
        db.execute('''
            INSERT INTO bookings (
                booking_reference, user_id, flight_id, passenger_name,
                passenger_age, passenger_gender, contact_number,
                seat_number, status, total_fare
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
        ''', (pnr, session['user_id'], flight_id, passenger_name, passenger_age, passenger_gender, contact_number, selected_seat, total_fare))

        # Decrement available seats count on the flight
        db.execute('''
            UPDATE flights 
            SET available_seats = available_seats - 1 
            WHERE id = ? AND available_seats > 0
        ''', (flight_id,))

        db.commit()

        flash(f"Booking Confirmed! Your PNR reference is {pnr}.", "success")
        return redirect(url_for('my_bookings'))

    return render_template(
        'booking.html', 
        flight=flight, 
        seat_layout=seat_layout, 
        booked_seats=booked_seats
    )


@app.route('/my-bookings')
@login_required
def my_bookings():
    """Displays all bookings made by the logged-in user."""
    db = get_db()
    user_bookings = db.execute('''
        SELECT 
            b.*,
            f.flight_number, f.airline, f.source, f.destination,
            f.departure_time, f.arrival_time, f.flight_date, f.duration
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC
    ''', (session['user_id'],)).fetchall()

    return render_template('my_bookings.html', bookings=user_bookings)


@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """
    Cancels an active booking:
    - Updates status to 'Cancelled'
    - Restores the available seat count on the flight
    - Ensures user only cancels their own booking (or admin)
    """
    db = get_db()
    booking = db.execute('''
        SELECT b.*, f.id AS flight_id 
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.id = ?
    ''', (booking_id,)).fetchone()

    if not booking:
        flash("Booking record not found.", "danger")
        return redirect(url_for('my_bookings'))

    # Security check: User can only cancel their own booking, unless Admin
    if booking['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        flash("Unauthorized action.", "danger")
        return redirect(url_for('my_bookings'))

    if booking['status'] == 'Cancelled':
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for('my_bookings'))

    # Update status to Cancelled
    db.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = ?", (booking_id,))

    # Increase available seats count on the flight
    db.execute('''
        UPDATE flights 
        SET available_seats = available_seats + 1 
        WHERE id = ? AND available_seats < total_seats
    ''', (booking['flight_id'],))

    db.commit()

    flash(f"Booking {booking['booking_reference']} has been cancelled successfully.", "success")
    if session.get('user_role') == 'admin' and request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('my_bookings'))


@app.route('/ticket/<int:booking_id>')
@login_required
def view_ticket(booking_id):
    """Displays a printable e-Ticket / Boarding Pass for a booking."""
    db = get_db()
    booking = db.execute('''
        SELECT 
            b.*,
            f.flight_number, f.airline, f.source, f.destination,
            f.departure_time, f.arrival_time, f.flight_date, f.duration,
            u.name as booked_by_name, u.email as booked_by_email
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        JOIN users u ON b.user_id = u.id
        WHERE b.id = ?
    ''', (booking_id,)).fetchone()

    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for('my_bookings'))

    # Security check: ensure user owns this ticket or is admin
    if booking['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        flash("Unauthorized access to ticket.", "danger")
        return redirect(url_for('my_bookings'))

    return render_template('ticket.html', booking=booking)


# ==========================================
# ADMIN DASHBOARD ROUTES
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin Dashboard:
    - High-level system statistics (Flights, Bookings, Users, Revenue).
    - Flight Management (Add/Edit/Delete).
    - All System Bookings with status.
    - Registered Users directory.
    """
    db = get_db()

    # Calculate statistics
    total_flights = db.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    total_bookings = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    confirmed_bookings = db.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'").fetchone()[0]
    total_users = db.execute("SELECT COUNT(*) FROM users WHERE role = 'user'").fetchone()[0]
    total_revenue_row = db.execute("SELECT SUM(total_fare) FROM bookings WHERE status = 'Confirmed'").fetchone()
    total_revenue = total_revenue_row[0] if total_revenue_row[0] else 0.0

    # Fetch all flights
    all_flights = db.execute("SELECT * FROM flights ORDER BY flight_date ASC, departure_time ASC").fetchall()

    # Fetch all bookings with user and flight details
    all_bookings = db.execute('''
        SELECT 
            b.*,
            f.flight_number, f.source, f.destination, f.flight_date,
            u.name AS user_name, u.email AS user_email
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    ''').fetchall()

    # Fetch all registered users
    all_users = db.execute('''
        SELECT id, name, email, phone, role, created_at,
               (SELECT COUNT(*) FROM bookings WHERE user_id = users.id) as booking_count
        FROM users 
        ORDER BY created_at DESC
    ''').fetchall()

    stats = {
        'total_flights': total_flights,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_users': total_users,
        'total_revenue': total_revenue
    }

    cities = get_all_cities()

    return render_template(
        'admin.html',
        stats=stats,
        flights=all_flights,
        bookings=all_bookings,
        users=all_users,
        cities=cities
    )


@app.route('/admin/flight/add', methods=['POST'])
@admin_required
def admin_add_flight():
    """Allows admin to add a new scheduled flight."""
    flight_number = request.form.get('flight_number', '').strip().upper()
    airline = request.form.get('airline', '').strip()
    source = request.form.get('source', '').strip()
    destination = request.form.get('destination', '').strip()
    departure_time = request.form.get('departure_time', '').strip()
    arrival_time = request.form.get('arrival_time', '').strip()
    flight_date = request.form.get('flight_date', '').strip()
    duration = request.form.get('duration', '').strip()
    total_seats = request.form.get('total_seats', '60').strip()
    price = request.form.get('price', '').strip()

    if not all([flight_number, airline, source, destination, departure_time, arrival_time, flight_date, duration, price]):
        flash("All flight fields are required.", "danger")
        return redirect(url_for('admin_dashboard'))

    if source.lower() == destination.lower():
        flash("Source and destination cities cannot be identical.", "warning")
        return redirect(url_for('admin_dashboard'))

    db = get_db()

    # Check if flight number already exists
    existing = db.execute("SELECT id FROM flights WHERE flight_number = ?", (flight_number,)).fetchone()
    if existing:
        flash(f"Flight number '{flight_number}' already exists.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        total_seats = int(total_seats)
        price = float(price)
    except ValueError:
        flash("Seats and price must be valid numeric values.", "danger")
        return redirect(url_for('admin_dashboard'))

    db.execute('''
        INSERT INTO flights (
            flight_number, airline, source, destination, 
            departure_time, arrival_time, flight_date, 
            duration, total_seats, available_seats, price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (flight_number, airline, source, destination, departure_time, arrival_time, flight_date, duration, total_seats, total_seats, price))
    db.commit()

    flash(f"Flight {flight_number} added successfully!", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/flight/edit/<int:flight_id>', methods=['POST'])
@admin_required
def admin_edit_flight(flight_id):
    """Allows admin to update flight timing, seats, and price."""
    airline = request.form.get('airline', '').strip()
    source = request.form.get('source', '').strip()
    destination = request.form.get('destination', '').strip()
    departure_time = request.form.get('departure_time', '').strip()
    arrival_time = request.form.get('arrival_time', '').strip()
    flight_date = request.form.get('flight_date', '').strip()
    duration = request.form.get('duration', '').strip()
    price = request.form.get('price', '').strip()

    if not all([airline, source, destination, departure_time, arrival_time, flight_date, duration, price]):
        flash("All fields are required to update the flight.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        price = float(price)
    except ValueError:
        flash("Price must be a valid number.", "danger")
        return redirect(url_for('admin_dashboard'))

    db = get_db()
    db.execute('''
        UPDATE flights 
        SET airline = ?, source = ?, destination = ?, departure_time = ?, 
            arrival_time = ?, flight_date = ?, duration = ?, price = ?
        WHERE id = ?
    ''', (airline, source, destination, departure_time, arrival_time, flight_date, duration, price, flight_id))
    db.commit()

    flash("Flight details updated successfully.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/flight/delete/<int:flight_id>', methods=['POST'])
@admin_required
def admin_delete_flight(flight_id):
    """
    Deletes a flight only if it does not have any active/confirmed bookings.
    Requirement: Delete flights without existing bookings.
    """
    db = get_db()

    # Check for active bookings
    active_bookings = db.execute('''
        SELECT COUNT(*) FROM bookings 
        WHERE flight_id = ? AND status = 'Confirmed'
    ''', (flight_id,)).fetchone()[0]

    if active_bookings > 0:
        flash(f"Cannot delete flight! It currently has {active_bookings} active confirmed booking(s).", "danger")
        return redirect(url_for('admin_dashboard'))

    # If only cancelled bookings exist or no bookings at all, we can safely delete
    db.execute("DELETE FROM bookings WHERE flight_id = ?", (flight_id,))
    db.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
    db.commit()

    flash("Flight deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == '__main__':
    # Initialize SQLite database and sample records
    init_db()
    print("=" * 60)
    print(" SkyBook Airlines - Airline Reservation System ")
    print(" Server running at: http://127.0.0.1:5000")
    print(" Admin Login: admin@skybook.com | admin123")
    print(" User Login:  rahul@gmail.com    | user123")
    print("=" * 60)
    app.run(debug=True, port=5000)
