"""
Quick Launcher for SkyBook Airlines
Allows running: python app.py or python run.py
"""
import app

if __name__ == '__main__':
    app.init_db()
    print("=" * 60)
    print(" SkyBook Airlines - Airline Reservation System ")
    print(" Server running at: http://127.0.0.1:5000")
    print(" Admin Login: admin@skybook.com | admin123")
    print(" User Login:  rahul@gmail.com    | user123")
    print("=" * 60)
    app.app.run(debug=True, port=5000)
