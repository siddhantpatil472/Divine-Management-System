# Divine Management System - Flask + MySQL Backend

This backend is designed for the React frontend in the parent folder and MySQL supplied by XAMPP.

## 1. Start MySQL in XAMPP
Open XAMPP Control Panel and start **MySQL**. Apache is not required for the Flask API.

## 2. Create the database
Open **phpMyAdmin** from XAMPP, choose **Import**, select `schema.sql`, and run it.

## 3. Install Python packages
Open a terminal in this `backend` folder:

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if needed. The default XAMPP MySQL account is `root` with an empty password.

## 4. Start the API
```bash
python app.py
```
The API runs at `http://127.0.0.1:5000`.

You can also double-click `run.bat` on Windows.

## Main endpoints
- `GET /api/health`
- `GET /api/temples`
- `GET /api/events`
- `POST /api/bookings`
- `POST /api/donations`
- `POST /api/complaints`
- `POST /api/event-registrations`

The backend enforces 10 Darshan persons per temple/date and 50 rooms per temple for overlapping stays.
