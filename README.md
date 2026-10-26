# SkyBook Airlines — Complete Airline Reservation System

## Project Overview

Build a complete, functional, beginner-friendly full-stack web application named **SkyBook Airlines**, an Airline Reservation System designed for a college Software Engineering (SE) Lab Mini-Project.

The application must look like a professional airline booking website, with a clean blue-and-white visual theme, modern layouts, responsive pages, interactive components, and a simple user experience.

**Important:** Build the actual working application, not a prototype, static mockup, project description, or collection of disconnected HTML pages. Every major button, form, navigation link, and user workflow must work correctly.

## 1. Technology Stack

Use only the following technologies:

- **Frontend:** HTML5, CSS3, JavaScript (ES6)
- **CSS Framework:** Bootstrap 5.3
- **Icons:** Bootstrap Icons
- **Backend:** Python Flask 3.x
- **Database:** SQLite3
- **Templating:** Jinja2
- **Authentication:** Flask sessions and Werkzeug password hashing

Do not use React, Next.js, Node.js, TypeScript, MongoDB, or any unnecessary frameworks.

The project must be straightforward to install and run locally using Python and pip.

## 2. Design and User Experience

Create a polished, professional airline website inspired by modern flight-booking platforms.

### Visual Direction

- Primary colors: airline blue, white, and subtle light-gray backgrounds.
- Use a consistent blue color palette with restrained accent colors.
- Use clean typography, preferably Inter or a similar modern sans-serif font.
- Include spacious layouts, rounded cards, subtle shadows, and consistent spacing.
- Use Bootstrap Icons for navigation, flights, passengers, bookings, and administration.
- Add subtle hover states, transitions, and loading or empty states where appropriate.
- Ensure all pages are responsive across desktop, tablet, and mobile.
- Maintain accessible labels, readable contrast, and clear validation messages.

Avoid excessive gradients, unnecessary animations, cluttered layouts, and generic unstyled forms.

### Shared Website Layout

Create a reusable base template containing:

- Responsive navigation bar
- SkyBook Airlines branding and airplane icon
- Navigation links appropriate to the current authentication state
- Login, registration, or account actions
- Flash-message notifications
- Consistent page content area
- Footer with basic airline information and navigation links

The navigation must adapt according to whether the visitor is logged in as a customer or an administrator.

## 3. Customer-Facing Features

### A. Homepage

Create an attractive homepage containing:

- Hero section with an airline-themed headline and supporting text.
- Flight search form.
- Origin and destination selection.
- Departure date selector.
- Passenger count selector if supported by the booking workflow.
- Search button.
- Popular domestic Indian routes.
- Featured flight offers or informational cards.
- A brief explanation of the booking process.
- Professional footer.

Seed the application with realistic sample routes connecting cities such as Ahmedabad, Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Kolkata, and Goa.

The homepage search form must submit real data to the Flask backend.

### B. User Registration

Implement a working registration system with:

- Full name
- Email address
- Phone number
- Password
- Confirm password

Requirements:

- Validate all required fields on the client and server.
- Validate email format and password requirements.
- Prevent duplicate email registrations.
- Store only password hashes, never plaintext passwords.
- Show useful success and error messages.
- Redirect successfully registered users to the appropriate page.

### C. Login and Logout

Create a clean login page with:

- Email address
- Password
- Login button
- Registration link
- Demo Customer autofill button
- Demo Administrator autofill button

Authenticate users securely using Werkzeug password-hashing utilities.

Use server-side sessions to maintain authentication state. Implement logout and ensure protected pages cannot be accessed after the session ends.

Never expose password hashes in templates or API responses.

### D. Flight Search

Allow customers to search flights using:

- Origin city
- Destination city
- Departure date

Display matching flights as clean, informative cards.

Each card should show:

- Airline name and flight number
- Origin and destination
- Departure and arrival times
- Flight duration
- Travel date
- Available seats
- Ticket price
- Select Seats / Book Flight button

Include sorting by price, low to high, and high to low.

Requirements:

- Do not show flights where the origin and destination are identical.
- Filter using the selected travel date.
- Validate search inputs on the backend.
- Display a useful empty state when no flights match.
- Calculate availability from actual confirmed bookings rather than blindly trusting a counter.
- Prevent booking flights that have already departed or are otherwise ineligible for travel.

### E. Interactive Aircraft Seat Selection

Build an interactive 60-seat aircraft layout inspired by an Airbus A320, using a 3-aisle-3 configuration: three seats on each side of the aisle.

Use a layout such as:

A B C | aisle | D E F

Display 10 rows with six seats per row, numbered 1 through 10.

Provide a legend for:

- Available seats
- Currently selected seat
- Already booked seats

Requirements:

- Available seats must be clickable.
- Selected seats must be visually distinct.
- Confirmed booked seats must be disabled.
- Display the selected seat number clearly.
- Display the total fare before confirmation.
- Refresh or validate seat availability before saving a booking.
- If another user books the same seat first, reject the duplicate booking and display an appropriate message.
- Do not allow a customer to submit a booking without selecting a seat.

The backend must be the final authority for seat availability. Frontend JavaScript alone must never determine whether a seat can be booked.

### F. Passenger Details and Booking Confirmation

After selecting a seat, present a passenger details form containing:

- Passenger full name
- Age
- Gender
- Contact number

Validate the fields and submit the booking to Flask.

On successful booking:

- Generate a unique six-character alphanumeric booking reference (PNR).
- Save the passenger and flight information.
- Record the selected seat.
- Store the total fare.
- Set the booking status to `Confirmed`.
- Update or recalculate available seats correctly.
- Show a confirmation message.
- Redirect to the booking details or e-ticket page.

Use a database transaction to ensure that booking creation and availability updates succeed together.

Handle concurrent booking attempts safely. Add a database-level uniqueness safeguard for active reservations, where appropriate, and implement a reliable transaction strategy for SQLite.

### G. My Bookings

Create a dedicated customer dashboard at `/my-bookings`.

Display the logged-in customer's bookings with:

- PNR reference
- Flight number
- Airline
- Route
- Departure date and time
- Passenger name
- Seat number
- Total fare
- Booking status

Provide actions to:

- View E-Ticket
- Print Ticket
- Cancel Booking when eligible

Customers must only be able to view and cancel their own bookings.

Include appropriate empty states when the customer has no bookings.

### H. E-Ticket and Boarding Pass

Create a professional, printable boarding-pass-style ticket.

Display:

- SkyBook Airlines branding
- Passenger name
- PNR reference
- Flight number
- Origin and destination
- Travel date
- Departure and arrival times
- Seat number
- Passenger details
- Total fare
- Booking status
- A visually styled barcode or PNR representation

The ticket must be printable and support saving as PDF using the browser's print dialog.

Use print-specific CSS to remove navigation, buttons, and unnecessary screen elements when printing.

Do not represent a decorative barcode as a scannable barcode unless it is generated correctly. A simple styled PNR code is acceptable for this academic project.

Cancelled bookings must clearly display their cancelled status.

### I. Booking Cancellation

Implement a working cancellation process.

Before cancellation, show a confirmation dialog explaining which booking will be cancelled.

When cancellation is confirmed:

- Verify that the logged-in user owns the booking, unless the administrator is performing an authorized action.
- Verify that the booking is currently confirmed.
- Update its status to `Cancelled`.
- Make the seat available for future reservations.
- Keep the booking record for audit purposes.
- Update availability consistently within a database transaction.
- Prevent repeated cancellation from incrementing seat availability multiple times.

Use appropriate flash messages and redirects.

## 4. Administrator Dashboard

Create a protected administration dashboard at `/admin`.

Only authenticated users with the `admin` role may access administrative pages and actions.

### A. Dashboard Statistics

Display summary cards for:

- Total flights
- Total registered users
- Confirmed bookings
- Cancelled bookings
- Total revenue from confirmed bookings

Calculate statistics using real database queries.

Cancelled bookings must not contribute to confirmed-booking revenue.

### B. Flight Management

Create a flight-management table showing:

- Flight number
- Airline
- Origin
- Destination
- Travel date
- Departure time
- Arrival time
- Total seats
- Available seats
- Fare

Implement the following functions:

1. Add a new flight.
2. Edit flight details.
3. Update departure and arrival times.
4. Update fares.
5. Delete eligible flights.

The add/edit form must include all required flight fields and validate them on the server.

Prevent duplicate flight numbers.

Do not allow deletion of flights with confirmed bookings. Cancelled booking records should not be silently destroyed.

If flight schedules are changed, ensure the departure and arrival times and dates remain consistent.

### C. Booking Management

Provide an administrative booking table showing:

- PNR
- Customer account
- Passenger name
- Flight
- Seat
- Fare
- Booking date
- Status

Allow administrators to inspect bookings and cancel confirmed bookings when necessary.

Use POST requests for state-changing operations and require appropriate authorization.

### D. User Management

Provide an administrator view of registered users, including:

- User name
- Email
- Phone number
- Account role
- Registration date

Do not display password hashes.

Do not allow customers to access this information.

## 5. Database Design

Use SQLite3 with three primary relational tables.

### Table 1: `users`

Fields:

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `email`: TEXT UNIQUE NOT NULL
- `password_hash`: TEXT NOT NULL
- `phone`: TEXT
- `role`: TEXT NOT NULL DEFAULT 'user'
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Restrict roles to `user` and `admin`.

### Table 2: `flights`

Fields:

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `flight_number`: TEXT UNIQUE NOT NULL
- `airline`: TEXT NOT NULL
- `source`: TEXT NOT NULL
- `destination`: TEXT NOT NULL
- `departure_time`: TEXT NOT NULL
- `arrival_time`: TEXT NOT NULL
- `flight_date`: TEXT NOT NULL
- `duration`: TEXT NOT NULL
- `total_seats`: INTEGER NOT NULL DEFAULT 60
- `price`: REAL NOT NULL

Store travel dates in `YYYY-MM-DD` format.

Use validated time values and consistent formatting. Ensure the total number of seats is positive and the fare is nonnegative.

Calculate availability from confirmed bookings or maintain a synchronized availability field with transaction-safe updates. Do not allow the stored value to drift from the actual booking records.

### Table 3: `bookings`

Fields:

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `booking_reference`: TEXT UNIQUE NOT NULL
- `user_id`: INTEGER NOT NULL
- `flight_id`: INTEGER NOT NULL
- `passenger_name`: TEXT NOT NULL
- `passenger_age`: INTEGER NOT NULL
- `passenger_gender`: TEXT NOT NULL
- `contact_number`: TEXT NOT NULL
- `seat_number`: TEXT NOT NULL
- `booking_date`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `status`: TEXT NOT NULL DEFAULT 'Confirmed'
- `total_fare`: REAL NOT NULL

Add foreign-key constraints referencing `users.id` and `flights.id`.

Restrict booking status to `Confirmed` and `Cancelled`.

Add appropriate indexes to improve queries for confirmed bookings, flight availability, and user booking history.

Ensure that two confirmed bookings cannot reserve the same seat on the same flight. Use an appropriate SQLite partial unique index or an equivalent transaction-safe database constraint.

Enable foreign-key enforcement for every SQLite connection.

## 6. Security Requirements

Implement security appropriate for a college-level full-stack project.

- Hash passwords with Werkzeug.
- Use parameterized SQL queries throughout.
- Never concatenate untrusted input into SQL statements.
- Protect routes using authentication and role-based authorization.
- Enforce ownership checks for individual bookings.
- Validate all important input on the backend.
- Use POST for operations that change database state.
- Add CSRF protection for forms, including cancellation and administrative actions.
- Use secure session settings and a configurable secret key.
- Set `HttpOnly` and appropriate `SameSite` cookie settings.
- Never expose secrets or database credentials in frontend code.
- Handle missing records and unauthorized requests safely.
- Display useful error messages without exposing internal stack traces.
- Avoid unsafe template rendering of user-provided content.

For local development, use a development secret key only when no environment variable is configured. Document that a strong secret must be supplied for deployment.

Do not claim the project is production-ready merely because it includes these protections.

## 7. Recommended Project Structure

Create the following structure:

```text
airline-reservation-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── database/
│   └── .gitkeep
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── flights.html
│   ├── booking.html
│   ├── my_bookings.html
│   ├── ticket.html
│   ├── admin.html
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── img/
```

The SQLite database should be generated automatically on first run. Do not require the user to create the database manually.

You may organize the Flask application into additional modules if this improves maintainability, but keep the setup beginner-friendly.

## 8. Sample Data and Demo Accounts

On the first run, initialize the database with realistic sample domestic flights and demo accounts.

Create these accounts if they do not already exist:

**Administrator**

- Email: `admin@skybook.com`
- Password: `admin123`
- Role: `admin`

**Demo Customer**

- Email: `rahul@gmail.com`
- Password: `user123`
- Role: `user`

Hash both passwords before storing them.

Make initialization idempotent so that restarting the application does not duplicate sample flights or users.

If demo bookings are included, ensure that their seats and availability are consistent.

These are demonstration credentials only and must be clearly identified as unsuitable for production.

## 9. Installation and Execution

Create a complete `requirements.txt` containing every required external Python dependency, including Flask and any libraries used for CSRF protection or environment-variable loading.

The project must run using these commands:

```bash
cd airline-reservation-system

python -m venv venv
```

Activate the environment.

Windows Command Prompt:

```bash
venv\Scripts\activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

Open:

`http://127.0.0.1:5000`

Document common installation errors and their solutions in `README.md`.

Use Flask's development server only for local development.

## 10. Software Engineering Documentation

Create a complete `README.md` covering:

1. Project introduction
2. Objectives and scope
3. Technology stack
4. System architecture
5. Project directory structure
6. Database schema
7. Installation instructions
8. Demo credentials
9. Application features
10. Functional requirements
11. Nonfunctional requirements
12. Security measures
13. Test cases and expected results
14. Known limitations
15. Future enhancements
16. Software Engineering viva questions and answers

Include a concise explanation of the Model-Template-View architecture used by Flask, database relationships, session management, password hashing, SQL injection prevention, and transaction-safe seat booking.

Do not claim that tests have passed unless they have actually been executed.

## 11. Required Functional Testing

Verify the following workflows before considering the project complete:

1. Homepage loads successfully.
2. Registration creates a user with a hashed password.
3. Duplicate email registration is rejected.
4. Valid login succeeds and invalid login fails.
5. Customers cannot access the admin dashboard.
6. Administrators can access the admin dashboard.
7. Flight search returns matching flights.
8. Invalid or identical origin and destination values are rejected.
9. Available seats can be selected.
10. Confirmed booked seats cannot be reserved again.
11. A successful booking generates a unique PNR.
12. The ticket displays the correct passenger, flight, seat, and fare.
13. Customers cannot access another customer's bookings.
14. Cancellation changes the status and releases the seat exactly once.
15. Cancelled bookings remain in the database.
16. Administrators can add and edit flights.
17. Flights with confirmed bookings cannot be deleted.
18. Invalid form submissions are handled safely.
19. Database transactions prevent duplicate seat reservations under concurrent requests.
20. All major pages work on desktop and mobile.

Write automated tests for the critical authentication, authorization, booking, seat-uniqueness, and cancellation workflows where practical.

## 12. Suggested Software Engineering Viva Questions

Include clear, beginner-friendly answers to questions such as:

- What is an Airline Reservation System?
- What problem does this project solve?
- Why was Flask selected?
- Why is SQLite suitable for this mini-project?
- What is the MVC or Model-Template-View pattern?
- What is the purpose of Jinja2?
- How does session-based authentication work?
- What is password hashing?
- How does the system prevent SQL injection?
- How is double-booking prevented?
- Why are database transactions important?
- What is a primary key?
- What is a foreign key?
- What is referential integrity?
- Why is booking cancellation recorded instead of deleting the booking?
- What are functional and nonfunctional requirements?
- What testing techniques are used?
- What are the limitations of this project?
- How could the application be extended in the future?

Answers must be consistent with the actual implementation.

## 13. Final Implementation Instructions

Follow this execution order:

1. Create the complete project directory and all required files.
2. Implement the database schema and initialization logic.
3. Implement authentication, authorization, and session management.
4. Implement flight search and administration.
5. Implement seat selection and transaction-safe booking.
6. Implement booking history, ticket generation, and cancellation.
7. Build all HTML templates and responsive styling.
8. Add JavaScript for interactive behavior and client-side validation.
9. Add security protections and error handling.
10. Create documentation and test cases.
11. Run the application and execute the available tests.
12. Fix errors found during testing.

### Non-negotiable requirements

- Generate actual working source files, not just code snippets or a written plan.
- Do not leave core functionality as TODO comments or placeholder buttons.
- Do not fabricate successful test results.
- Do not implement seat availability solely in JavaScript.
- Do not allow users to bypass server-side authorization.
- Do not store plaintext passwords.
- Do not silently lose booking records during cancellation.
- Do not create duplicate demo accounts or flights on repeated startup.
- Keep the project easy for a college student to understand, demonstrate, and explain during a viva.

**Final deliverable:** A complete, runnable SkyBook Airlines web application with source code, database initialization, sample data, demo accounts, responsive interface, functional booking workflows, administrator dashboard, documentation, and working tests.

When implementation is complete, provide a concise summary of the files created, installation commands, demo credentials, features implemented, and tests actually executed.
