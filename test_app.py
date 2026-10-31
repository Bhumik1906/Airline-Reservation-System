"""
Automated Test Suite for SkyBook Airlines
Validates all requirements: Auth, Search, Seat Map, Double-Booking Prevention,
Cancellation, Admin Controls, and Database Integrity.
"""

import unittest
import sqlite3
import os
import sys

# Ensure airline-reservation-system is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, init_db, get_db
from werkzeug.security import check_password_hash

class AirlineSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and configure test mode."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_01_database_tables_and_seed_data(self):
        """Verify database tables and initial seeded data exist."""
        with app.app_context():
            db = get_db()
            users_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            flights_count = db.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
            bookings_count = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]

            self.assertGreaterEqual(users_count, 2, "Should have at least 2 seeded users")
            self.assertGreaterEqual(flights_count, 10, "Should have seeded flights")
            self.assertGreaterEqual(bookings_count, 1, "Should have seeded bookings")
            print("[PASS] Test 1: Database schema and seed data verified.")

    def test_02_homepage_and_flights_page(self):
        """Verify homepage and flight search page render successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SkyBook", response.data)
        self.assertIn(b"Search Domestic Flights", response.data)

        response = self.client.get('/flights?source=Ahmedabad&destination=Mumbai')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ahmedabad", response.data)
        self.assertIn(b"Mumbai", response.data)
        print("[PASS] Test 2: Homepage and Flight search pages respond correctly.")

    def test_03_user_registration_and_login(self):
        """Test registering a new account and logging in."""
        import random
        rand_id = random.randint(1000, 9999)
        test_email = f"testuser{rand_id}@example.com"
        
        # 1. Register
        reg_response = self.client.post('/register', data={
            'name': 'Test Passenger',
            'email': test_email,
            'phone': '9998887776',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Registration successful", reg_response.data)

        # 2. Login
        login_response = self.client.post('/login', data={
            'email': test_email,
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b"Welcome back, Test Passenger", login_response.data)

        # 3. Check session
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['user_email'], test_email)
            self.assertEqual(sess['user_role'], 'user')

        print("[PASS] Test 3: User registration and secure login working.")

    def test_04_seat_booking_and_double_booking_prevention(self):
        """Test seat reservation and ensure same seat cannot be booked twice."""
        # Login demo user
        self.client.post('/login', data={'email': 'rahul@gmail.com', 'password': 'user123'})

        with app.app_context():
            db = get_db()
            flight = db.execute("SELECT id, available_seats FROM flights WHERE available_seats > 5 LIMIT 1").fetchone()
            flight_id = flight['id']
            initial_seats = flight['available_seats']

            # Find an unbooked seat
            booked = [r[0] for r in db.execute("SELECT seat_number FROM bookings WHERE flight_id = ? AND status = 'Confirmed'", (flight_id,)).fetchall()]
            all_possible = [f"{r}{c}" for r in range(1, 11) for c in ['A', 'B', 'C', 'D', 'E', 'F']]
            target_seat = next(s for s in all_possible if s not in booked)

        # Book the target seat
        book_res = self.client.post(f'/book/{flight_id}', data={
            'passenger_name': 'Aarav Patel',
            'passenger_age': '28',
            'passenger_gender': 'Male',
            'contact_number': '9876501234',
            'seat_number': target_seat
        }, follow_redirects=True)
        self.assertEqual(book_res.status_code, 200)
        self.assertIn(b"Booking Confirmed", book_res.data)

        with app.app_context():
            db = get_db()
            updated_flight = db.execute("SELECT available_seats FROM flights WHERE id = ?", (flight_id,)).fetchone()
            self.assertEqual(updated_flight['available_seats'], initial_seats - 1)

        # Attempt to book the exact same seat on the same flight - MUST FAIL
        duplicate_res = self.client.post(f'/book/{flight_id}', data={
            'passenger_name': 'Another Person',
            'passenger_age': '30',
            'passenger_gender': 'Female',
            'contact_number': '9876501234',
            'seat_number': target_seat
        }, follow_redirects=True)
        self.assertIn(b"already booked", duplicate_res.data)
        print("[PASS] Test 4: Seat reservation works and double-booking is strictly prevented.")

    def test_05_booking_cancellation_and_seat_restoration(self):
        """Test canceling a booking and verify seat is returned to flight."""
        # Login demo user
        self.client.post('/login', data={'email': 'rahul@gmail.com', 'password': 'user123'})

        with app.app_context():
            db = get_db()
            # Find a confirmed booking
            booking = db.execute("SELECT id, flight_id FROM bookings WHERE status = 'Confirmed' LIMIT 1").fetchone()
            booking_id = booking['id']
            flight_id = booking['flight_id']

            flight_before = db.execute("SELECT available_seats FROM flights WHERE id = ?", (flight_id,)).fetchone()
            seats_before = flight_before['available_seats']

        # Cancel the booking
        cancel_res = self.client.post(f'/cancel-booking/{booking_id}', follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertIn(b"cancelled successfully", cancel_res.data)

        with app.app_context():
            db = get_db()
            booking_after = db.execute("SELECT status FROM bookings WHERE id = ?", (booking_id,)).fetchone()
            self.assertEqual(booking_after['status'], 'Cancelled')

            flight_after = db.execute("SELECT available_seats FROM flights WHERE id = ?", (flight_id,)).fetchone()
            self.assertEqual(flight_after['available_seats'], seats_before + 1)

        print("[PASS] Test 5: Booking cancellation and seat restoration verified.")

    def test_06_admin_access_control_and_flight_management(self):
        """Test admin role restriction and admin CRUD capabilities."""
        # 1. Regular user trying to access /admin should be blocked
        self.client.post('/login', data={'email': 'rahul@gmail.com', 'password': 'user123'})
        regular_admin_res = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b"Access denied", regular_admin_res.data)

        # 2. Admin login
        self.client.get('/logout')
        admin_login = self.client.post('/login', data={'email': 'admin@skybook.com', 'password': 'admin123'}, follow_redirects=True)
        self.assertIn(b"Admin Control Center", admin_login.data)

        # 3. Admin adds a new flight
        add_flight_res = self.client.post('/admin/flight/add', data={
            'flight_number': 'SB-999',
            'airline': 'SkyBook Express',
            'source': 'Ahmedabad',
            'destination': 'Goa',
            'departure_time': '07:00 AM',
            'arrival_time': '08:45 AM',
            'flight_date': '2026-11-15',
            'duration': '1h 45m',
            'total_seats': '60',
            'price': '3400'
        }, follow_redirects=True)
        self.assertIn(b"added successfully", add_flight_res.data)

        # 4. Verify flight was added
        with app.app_context():
            db = get_db()
            f = db.execute("SELECT * FROM flights WHERE flight_number = 'SB-999'").fetchone()
            self.assertIsNotNone(f)
            new_id = f['id']

        # 5. Admin edits the flight
        edit_flight_res = self.client.post(f'/admin/flight/edit/{new_id}', data={
            'airline': 'SkyBook Express Premium',
            'source': 'Ahmedabad',
            'destination': 'Goa',
            'departure_time': '07:30 AM',
            'arrival_time': '09:15 AM',
            'flight_date': '2026-11-15',
            'duration': '1h 45m',
            'price': '3600'
        }, follow_redirects=True)
        self.assertIn(b"updated successfully", edit_flight_res.data)

        # 6. Admin deletes the flight (has no bookings, so allowed)
        delete_flight_res = self.client.post(f'/admin/flight/delete/{new_id}', follow_redirects=True)
        self.assertIn(b"deleted successfully", delete_flight_res.data)

        print("[PASS] Test 6: Admin access control and flight CRUD verified.")

if __name__ == '__main__':
    unittest.main()
