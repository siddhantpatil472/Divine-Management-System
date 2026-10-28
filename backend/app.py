import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "divine_management"),
}

SECRET = os.getenv(
    "SECRET_KEY",
    "divine-student-project-secret-change-me"
)
serializer = URLSafeTimedSerializer(SECRET)

TRUSTEES = [
    ("siddhivinayak_trustee", "Siddhivinayak Trustee", "1", "Siddhivinayak@123"),
    ("kashi_trustee", "Kashi Vishwanath Trustee", "2", "Kashi@123"),
    ("tirumala_trustee", "Tirumala Trustee", "3", "Tirumala@123"),
    ("jagannath_trustee", "Jagannath Trustee", "4", "Jagannath@123"),
    ("somnath_trustee", "Somnath Trustee", "5", "Somnath@123"),
]


# --------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def close_db(conn, cursor=None):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def fail(message, status=400):
    return jsonify({"success": False, "message": message}), status


def require_fields(data, fields):
    return [
        field for field in fields
        if data.get(field) is None or data.get(field) == ""
    ]


def ensure_column(cursor, table, column, definition):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s
        AND TABLE_NAME=%s
        AND COLUMN_NAME=%s
        """,
        (DB_CONFIG["database"], table, column),
    )

    if cursor.fetchone()[0] == 0:
        cursor.execute(
            f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
        )


def ensure_database():
    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Booking workflow fields
        ensure_column(cursor, "bookings", "status", "VARCHAR(30) DEFAULT 'PENDING'")
        ensure_column(cursor, "bookings", "ticket_no", "VARCHAR(40) NULL")
        ensure_column(cursor, "bookings", "confirmed_at", "DATETIME NULL")
        ensure_column(cursor, "bookings", "user_message", "VARCHAR(255) NULL")

        # Donation workflow fields
        ensure_column(cursor, "donations", "status", "VARCHAR(30) DEFAULT 'PENDING'")
        ensure_column(cursor, "donations", "receipt_no", "VARCHAR(40) NULL")
        ensure_column(cursor, "donations", "confirmed_at", "DATETIME NULL")
        ensure_column(cursor, "donations", "user_message", "VARCHAR(255) NULL")

        # Event management fields
        ensure_column(cursor, "events", "event_time", "VARCHAR(40) NULL")
        ensure_column(cursor, "events", "status", "VARCHAR(20) DEFAULT 'OPEN'")
        ensure_column(cursor, "events", "created_by", "INT NULL")

        # Keep older events visible unless already closed
        cursor.execute(
            """
            UPDATE events
            SET status='OPEN'
            WHERE status IS NULL OR status=''
            """
        )

        # Trustees
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trustees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                display_name VARCHAR(120) NOT NULL,
                temple_id VARCHAR(50) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                active TINYINT(1) DEFAULT 1,
                location VARCHAR(150) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)

        ensure_column(cursor, "trustees", "location", "VARCHAR(150) NULL")

        # Payments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT NULL,
                donation_id INT NULL,
                temple_id VARCHAR(50) NOT NULL,
                payer_name VARCHAR(120) NOT NULL,
                payer_phone VARCHAR(20) NOT NULL,
                payer_email VARCHAR(160) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                method VARCHAR(30) NOT NULL DEFAULT 'UPI',
                transaction_id VARCHAR(120) NOT NULL,
                payment_status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
                paid_at DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_payment_booking (booking_id),
                INDEX idx_payment_donation (donation_id),
                INDEX idx_payment_temple (temple_id)
            ) ENGINE=InnoDB
        """)

        # Notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                temple_id VARCHAR(50) NOT NULL,
                booking_id INT NULL,
                donation_id INT NULL,
                recipient_name VARCHAR(120) NOT NULL,
                recipient_phone VARCHAR(20) NOT NULL,
                recipient_email VARCHAR(160) NOT NULL,
                title VARCHAR(180) NOT NULL,
                message TEXT NOT NULL,
                reference_no VARCHAR(40) NULL,
                is_read TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_notification_phone (recipient_phone),
                INDEX idx_notification_email (recipient_email)
            ) ENGINE=InnoDB
        """)

        # Create trustee accounts only when they do not already exist.
        for username, display_name, temple_id, password in TRUSTEES:
            cursor.execute(
                "SELECT id FROM trustees WHERE username=%s",
                (username,),
            )

            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO trustees
                    (username, display_name, temple_id, password_hash)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        username,
                        display_name,
                        temple_id,
                        generate_password_hash(password),
                    ),
                )

        conn.commit()

    except Error as exc:
        print("Database initialization warning:", exc)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE AUTHENTICATION
# --------------------------------------------------

def make_token(trustee):
    return serializer.dumps({
        "trustee_id": trustee["id"],
        "temple_id": trustee["temple_id"],
        "username": trustee["username"],
    })


def get_trustee():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return None

    token_value = auth[7:].strip()

    try:
        data = serializer.loads(token_value, max_age=60 * 60 * 12)
    except (BadSignature, SignatureExpired):
        return None

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, username, display_name, temple_id, active
            FROM trustees
            WHERE id=%s AND active=1
            """,
            (data["trustee_id"],),
        )

        trustee = cursor.fetchone()

        # Confirm the token still belongs to this trustee and temple.
        if (
            not trustee
            or str(trustee["temple_id"]) != str(data["temple_id"])
        ):
            return None

        return trustee

    finally:
        close_db(conn, cursor)


def require_trustee():
    trustee = get_trustee()

    if not trustee:
        return None, fail(
            "Trustee login required or session expired",
            401,
        )

    return trustee, None


def reference(prefix, row_id):
    return f"{prefix}-{datetime.now().year}-{int(row_id):05d}"


def create_notification(
    cursor,
    *,
    temple_id,
    booking_id=None,
    donation_id=None,
    name,
    phone,
    email,
    title,
    message,
    ref,
):
    cursor.execute(
        """
        INSERT INTO notifications
        (
            temple_id, booking_id, donation_id,
            recipient_name, recipient_phone, recipient_email,
            title, message, reference_no
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            temple_id,
            booking_id,
            donation_id,
            name,
            phone,
            email,
            title,
            message,
            ref,
        ),
    )


# --------------------------------------------------
# HEALTH AND TEMPLES
# --------------------------------------------------

@app.get("/api/health")
def health():
    conn = None

    try:
        conn = get_db()

        return jsonify({
            "success": True,
            "message": "API and MySQL are connected",
        })

    except Error as exc:
        return fail(f"Database connection failed: {exc}", 500)

    finally:
        close_db(conn)


@app.get("/api/temples")
def temples():
    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, location, deity, history, image, services
            FROM temples
            ORDER BY id
        """)

        rows = cursor.fetchall()

        for row in rows:
            row["services"] = (
                row["services"].split(",")
                if row.get("services")
                else []
            )

        return jsonify({"success": True, "temples": rows})

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# PUBLIC EVENTS: ONLY OPEN EVENTS
# --------------------------------------------------

@app.get("/api/events")
def events():
    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id,
                e.title AS name,
                e.description,
                e.event_date,
                e.event_time,
                e.status,
                e.temple_id,
                t.name AS temple_name,
                t.location AS temple_location
            FROM events e
            LEFT JOIN temples t ON t.id = e.temple_id
            WHERE e.status = 'OPEN'
            ORDER BY e.event_date ASC, e.event_time ASC, e.id ASC
        """)

        return jsonify({
            "success": True,
            "events": cursor.fetchall(),
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE: ADD AN EVENT
# --------------------------------------------------

@app.post("/api/trustee/events")
def trustee_create_event():
    trustee, error = require_trustee()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    required = require_fields(
        data,
        ["title", "event_date", "event_time"],
    )

    if required:
        return fail("Missing fields: " + ", ".join(required))

    title = str(data["title"]).strip()

    if not title:
        return fail("Event title cannot be empty")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO events
            (
                title, description, event_date, event_time,
                temple_id, status, created_by
            )
            VALUES (%s, %s, %s, %s, %s, 'OPEN', %s)
        """, (
            title,
            data.get("description") or None,
            data["event_date"],
            data["event_time"],
            trustee["temple_id"],
            trustee["id"],
        ))

        event_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Event added successfully",
            "event_id": event_id,
            "status": "OPEN",
        }), 201

    except Error as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE: LIST ONLY THEIR TEMPLE'S EVENTS
# --------------------------------------------------

@app.get("/api/trustee/events")
def trustee_events():
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id,
                e.title AS name,
                e.description,
                e.event_date,
                e.event_time,
                e.status,
                e.temple_id,
                t.name AS temple_name
            FROM events e
            LEFT JOIN temples t ON t.id = e.temple_id
            WHERE e.temple_id=%s
            ORDER BY e.event_date ASC, e.event_time ASC, e.id DESC
        """, (trustee["temple_id"],))

        return jsonify({
            "success": True,
            "events": cursor.fetchall(),
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE: CLOSE AN EVENT
# --------------------------------------------------

@app.post("/api/trustee/events/<int:event_id>/close")
def trustee_close_event(event_id):
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, status
            FROM events
            WHERE id=%s AND temple_id=%s
        """, (event_id, trustee["temple_id"]))

        event = cursor.fetchone()

        if not event:
            return fail("Event not found for your temple", 404)

        if event["status"] == "CLOSED":
            return jsonify({
                "success": True,
                "message": "Event is already closed",
            })

        cursor.execute("""
            UPDATE events
            SET status='CLOSED'
            WHERE id=%s AND temple_id=%s
        """, (event_id, trustee["temple_id"]))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Event closed successfully",
        })

    except Error as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# BOOKINGS
# --------------------------------------------------

@app.post("/api/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}

    required = require_fields(
        data,
        ["booking_type", "name", "phone", "email"],
    )

    if required:
        return fail("Missing fields: " + ", ".join(required))

    booking_type = data["booking_type"]
    temple_id = data.get("temple_id") or None
    booking_date = data.get("date") or None

    try:
        persons = int(data.get("persons") or 1)
        rooms = int(data.get("rooms") or 0)
    except (ValueError, TypeError):
        return fail("Persons and rooms must be valid numbers")

    if persons < 1 or rooms < 0:
        return fail("Persons must be at least 1 and rooms cannot be negative")

    if persons > 5:
        return fail("Booking is allowed for up to 5 persons only")

    today_str = datetime.now().strftime("%Y-%m-%d")

    if booking_date and booking_date < today_str:
        return fail("Booking date must be today or a future date")

    if data.get("checkin") and data["checkin"] < today_str:
        return fail("Check-in date must be today or a future date")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor()

        if booking_type == "Darshan":
            if not temple_id or not booking_date:
                return fail("Temple and date are required for Darshan")

            cursor.execute("""
                SELECT COALESCE(SUM(persons),0)
                FROM bookings
                WHERE booking_type='Darshan'
                AND temple_id=%s
                AND date=%s
                AND status<>'REJECTED'
            """, (temple_id, booking_date))

            used = cursor.fetchone()[0]

            if used + persons > 10:
                return fail(
                    f"Darshan limit reached. Only {max(0, 10-used)} "
                    "persons remain for this temple and date."
                )

        if booking_type == "Room Booking":
            if (
                not temple_id
                or not data.get("checkin")
                or not data.get("checkout")
            ):
                return fail(
                    "Temple, check-in and check-out are required"
                )

            if data["checkout"] <= data["checkin"]:
                return fail("Check-out must be after check-in")

            cursor.execute("""
                SELECT COALESCE(SUM(rooms),0)
                FROM bookings
                WHERE booking_type='Room Booking'
                AND temple_id=%s
                AND status<>'REJECTED'
                AND checkin < %s
                AND checkout > %s
            """, (
                temple_id,
                data["checkout"],
                data["checkin"],
            ))

            used = cursor.fetchone()[0]

            if used + rooms > 50:
                return fail(
                    f"Room limit reached. Only {max(0, 50-used)} "
                    "rooms remain for these dates."
                )

        cursor.execute("""
            INSERT INTO bookings
            (
                booking_type, temple_id, date, slot, persons,
                pooja, checkin, checkout, rooms, meal,
                name, phone, email, event_name, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDING')
        """, (
            booking_type,
            temple_id,
            booking_date,
            data.get("slot") or None,
            persons,
            data.get("pooja") or None,
            data.get("checkin") or None,
            data.get("checkout") or None,
            rooms or None,
            data.get("meal") or None,
            data["name"],
            data["phone"],
            data["email"],
            data.get("event_name") or None,
        ))

        booking_id = cursor.lastrowid
        payment = data.get("payment") or {}

        if payment.get("transaction_id"):
            cursor.execute("""
                INSERT INTO payments
                (
                    booking_id, temple_id, payer_name, payer_phone,
                    payer_email, amount, method, transaction_id,
                    payment_status, paid_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'SUBMITTED',%s)
            """, (
                booking_id,
                temple_id or "",
                data["name"],
                data["phone"],
                data["email"],
                float(payment.get("amount") or 0),
                payment.get("method") or "UPI",
                payment["transaction_id"],
                payment.get("paid_at") or None,
            ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Booking submitted for trustee confirmation",
            "id": booking_id,
            "status": "PENDING",
        }), 201

    except (Error, ValueError, TypeError) as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# DONATIONS
# --------------------------------------------------

@app.post("/api/donations")
def create_donation():
    data = request.get_json(silent=True) or {}

    required = require_fields(
        data,
        ["temple_id", "name", "phone", "email", "amount", "purpose"],
    )

    if required:
        return fail("Missing fields: " + ", ".join(required))

    try:
        amount = float(data["amount"])
    except (ValueError, TypeError):
        return fail("Amount must be numeric")

    if amount <= 0:
        return fail("Amount must be greater than zero")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO donations
            (temple_id, name, phone, email, amount, purpose, status)
            VALUES (%s,%s,%s,%s,%s,%s,'PENDING')
        """, (
            data["temple_id"],
            data["name"],
            data["phone"],
            data["email"],
            amount,
            data["purpose"],
        ))

        donation_id = cursor.lastrowid
        payment = data.get("payment") or {}

        if payment.get("transaction_id"):
            cursor.execute("""
                INSERT INTO payments
                (
                    donation_id, temple_id, payer_name, payer_phone,
                    payer_email, amount, method, transaction_id,
                    payment_status, paid_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'SUBMITTED',%s)
            """, (
                donation_id,
                data["temple_id"],
                data["name"],
                data["phone"],
                data["email"],
                amount,
                payment.get("method") or "UPI",
                payment["transaction_id"],
                payment.get("paid_at") or None,
            ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Donation submitted for trustee confirmation",
            "id": donation_id,
            "status": "PENDING",
        }), 201

    except (Error, ValueError, TypeError) as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# EVENT REGISTRATION: OPEN EVENTS ONLY
# --------------------------------------------------

@app.post("/api/event-registrations")
def register_event():
    data = request.get_json(silent=True) or {}

    required = require_fields(
        data,
        ["event_id", "name", "phone", "email"],
    )

    if required:
        return fail("Missing fields: " + ", ".join(required))

    try:
        event_id = int(data["event_id"])
    except (ValueError, TypeError):
        return fail("A valid event_id is required")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, title, event_date, event_time, temple_id, status
            FROM events
            WHERE id=%s
        """, (event_id,))

        event = cursor.fetchone()

        if not event:
            return fail("Event not found", 404)

        if event["status"] != "OPEN":
            return fail("Registration for this event is closed", 400)

        # Save event details from the database, not from the request.
        cursor.execute("""
            INSERT INTO event_registrations
            (
                event_name, event_date, event_time, temple_id,
                name, phone, email
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            event["title"],
            event["event_date"] or None,
            event["event_time"] or None,
            event["temple_id"],
            data["name"],
            data["phone"],
            data["email"],
        ))

        registration_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Event registration saved",
            "id": registration_id,
        }), 201

    except Error as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE LOGIN
# --------------------------------------------------

@app.post("/api/trustee/login")
def trustee_login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return fail("Username and password are required")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, username, display_name, temple_id,
                   password_hash, active
            FROM trustees
            WHERE username=%s
        """, (username,))

        trustee = cursor.fetchone()

        if (
            not trustee
            or not trustee["active"]
            or not check_password_hash(trustee["password_hash"], password)
        ):
            return fail("Invalid trustee login", 401)

        token_value = make_token(trustee)

        cursor.execute(
            "SELECT name, location FROM temples WHERE id=%s",
            (trustee["temple_id"],),
        )

        temple = cursor.fetchone()

        return jsonify({
            "success": True,
            "token": token_value,
            "trustee": {
                "username": trustee["username"],
                "display_name": trustee["display_name"],
                "temple_id": trustee["temple_id"],
                "temple_name": (
                    temple["name"]
                    if temple
                    else trustee["temple_id"]
                ),
            },
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


@app.get("/api/trustee/me")
def trustee_me():
    trustee, error = require_trustee()

    if error:
        return error

    return jsonify({"success": True, "trustee": trustee})


# --------------------------------------------------
# TRUSTEE DASHBOARD: BOOKINGS AND DONATIONS
# --------------------------------------------------

@app.get("/api/trustee/dashboard")
def trustee_dashboard():
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        temple_id = trustee["temple_id"]

        cursor.execute("""
            SELECT
                b.*,
                p.id AS payment_id,
                p.amount AS payment_amount,
                p.method AS payment_method,
                p.transaction_id,
                p.payment_status,
                p.paid_at
            FROM bookings b
            LEFT JOIN payments p ON p.booking_id=b.id
            WHERE b.temple_id=%s
            ORDER BY b.id DESC
        """, (temple_id,))

        bookings = cursor.fetchall()

        cursor.execute("""
            SELECT
                d.*,
                p.id AS payment_id,
                p.amount AS payment_amount,
                p.method AS payment_method,
                p.transaction_id,
                p.payment_status,
                p.paid_at
            FROM donations d
            LEFT JOIN payments p ON p.donation_id=d.id
            WHERE d.temple_id=%s
            ORDER BY d.id DESC
        """, (temple_id,))

        donations = cursor.fetchall()

        stats = {
            "pending_bookings": sum(
                1 for b in bookings if b.get("status") == "PENDING"
            ),
            "confirmed_bookings": sum(
                1 for b in bookings if b.get("status") == "CONFIRMED"
            ),
            "pending_donations": sum(
                1 for d in donations if d.get("status") == "PENDING"
            ),
            "confirmed_donations": sum(
                1 for d in donations if d.get("status") == "CONFIRMED"
            ),
        }

        return jsonify({
            "success": True,
            "stats": stats,
            "bookings": bookings,
            "donations": donations,
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# CONFIRM BOOKING
# --------------------------------------------------

@app.post("/api/trustee/bookings/<int:booking_id>/confirm")
def confirm_booking(booking_id):
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM bookings
            WHERE id=%s AND temple_id=%s
        """, (booking_id, trustee["temple_id"]))

        booking = cursor.fetchone()

        if not booking:
            return fail("Booking not found for this temple", 404)

        if booking["status"] == "CONFIRMED":
            return jsonify({
                "success": True,
                "message": "Booking already confirmed",
                "reference_no": booking["ticket_no"],
            })

        ref = reference("TKT", booking_id)

        cursor.execute("""
            UPDATE bookings
            SET status='CONFIRMED',
                ticket_no=%s,
                confirmed_at=NOW(),
                user_message=%s
            WHERE id=%s AND temple_id=%s
        """, (
            ref,
            "Your booking has been confirmed by the temple trustee.",
            booking_id,
            trustee["temple_id"],
        ))

        create_notification(
            cursor,
            temple_id=trustee["temple_id"],
            booking_id=booking_id,
            name=booking["name"],
            phone=booking["phone"],
            email=booking["email"],
            title="Booking Confirmed",
            message=(
                f"Your {booking['booking_type']} booking has been confirmed. "
                f"Your ticket/reference number is {ref}."
            ),
            ref=ref,
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Booking confirmed and user notification created",
            "reference_no": ref,
        })

    except Error as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# CONFIRM DONATION
# --------------------------------------------------

@app.post("/api/trustee/donations/<int:donation_id>/confirm")
def confirm_donation(donation_id):
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM donations
            WHERE id=%s AND temple_id=%s
        """, (donation_id, trustee["temple_id"]))

        donation = cursor.fetchone()

        if not donation:
            return fail("Donation not found for this temple", 404)

        if donation["status"] == "CONFIRMED":
            return jsonify({
                "success": True,
                "message": "Donation already confirmed",
                "reference_no": donation["receipt_no"],
            })

        ref = reference("DON", donation_id)

        cursor.execute("""
            UPDATE donations
            SET status='CONFIRMED',
                receipt_no=%s,
                confirmed_at=NOW(),
                user_message=%s
            WHERE id=%s AND temple_id=%s
        """, (
            ref,
            "Your donation has been confirmed by the temple trustee.",
            donation_id,
            trustee["temple_id"],
        ))

        cursor.execute("""
            UPDATE payments
            SET payment_status='VERIFIED'
            WHERE donation_id=%s AND temple_id=%s
        """, (donation_id, trustee["temple_id"]))

        create_notification(
            cursor,
            temple_id=trustee["temple_id"],
            donation_id=donation_id,
            name=donation["name"],
            phone=donation["phone"],
            email=donation["email"],
            title="Donation Receipt Ready",
            message=(
                f"Your donation of ₹{donation['amount']} has been confirmed. "
                f"Your receipt number is {ref}."
            ),
            ref=ref,
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Donation confirmed and receipt notification created",
            "reference_no": ref,
        })

    except Error as exc:
        if conn:
            conn.rollback()
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# USER NOTIFICATIONS
# --------------------------------------------------

@app.get("/api/notifications")
def notifications():
    phone = request.args.get("phone", "").strip()
    email = request.args.get("email", "").strip()

    if not phone and not email:
        return fail("Enter your mobile number or email")

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        if phone and email:
            cursor.execute("""
                SELECT n.*, t.name AS temple_name
                FROM notifications n
                LEFT JOIN temples t ON t.id=n.temple_id
                WHERE n.recipient_phone=%s OR n.recipient_email=%s
                ORDER BY n.id DESC
            """, (phone, email))

        elif phone:
            cursor.execute("""
                SELECT n.*, t.name AS temple_name
                FROM notifications n
                LEFT JOIN temples t ON t.id=n.temple_id
                WHERE n.recipient_phone=%s
                ORDER BY n.id DESC
            """, (phone,))

        else:
            cursor.execute("""
                SELECT n.*, t.name AS temple_name
                FROM notifications n
                LEFT JOIN temples t ON t.id=n.temple_id
                WHERE n.recipient_email=%s
                ORDER BY n.id DESC
            """, (email,))

        return jsonify({
            "success": True,
            "notifications": cursor.fetchall(),
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# TRUSTEE PAYMENTS
# --------------------------------------------------

@app.get("/api/trustee/payments")
def trustee_payments():
    trustee, error = require_trustee()

    if error:
        return error

    conn = cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.*,
                b.booking_type,
                b.status AS booking_status,
                d.purpose,
                d.status AS donation_status
            FROM payments p
            LEFT JOIN bookings b ON b.id=p.booking_id
            LEFT JOIN donations d ON d.id=p.donation_id
            WHERE p.temple_id=%s
            ORDER BY p.id DESC
        """, (trustee["temple_id"],))

        return jsonify({
            "success": True,
            "payments": cursor.fetchall(),
        })

    except Error as exc:
        return fail(str(exc), 500)

    finally:
        close_db(conn, cursor)


# --------------------------------------------------
# 404 HANDLER
# --------------------------------------------------

@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "success": False,
        "message": "API route not found",
    }), 404


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    ensure_database()
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=True,
    )