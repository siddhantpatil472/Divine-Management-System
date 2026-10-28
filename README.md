# Divine Temple Management System — Full Stack

React + Vite frontend, Flask backend, and MySQL (XAMPP/phpMyAdmin).

## New trustee workflow

- Bhojan and Complaint have been removed from the navigation and application routes.
- Added **Trustee Login** for five temples.
- Each trustee account is locked to one temple. A trustee cannot view or confirm another temple's records.
- Trustees can see booking requests, donation requests, submitted payment/transaction details, and confirm them.
- After confirmation, the user receives an in-app notification containing a booking ticket number or donation receipt number.
- Users can open **My Notifications** and search with the mobile/email used for the request.
- Payment details are collected with transaction/UTR ID. The payment page uses the supplied UPI QR image.
- The backend automatically adds the new columns/tables to an existing `divine_management` database when it starts.

## Five trustee demo accounts

| Temple | Username | Password |
|---|---|---|
| Siddhivinayak | `siddhivinayak_trustee` | `Siddhivinayak@123` |
| Kashi Vishwanath | `kashi_trustee` | `Kashi@123` |
| Tirumala | `tirumala_trustee` | `Tirumala@123` |
| Jagannath | `jagannath_trustee` | `Jagannath@123` |
| Somnath | `somnath_trustee` | `Somnath@123` |

These are demo/student-project credentials. Change them before any real deployment.

## Run

### XAMPP

Start **Apache** and **MySQL**. Your database is:

`divine_management`

The existing database can be kept. The backend upgrades it automatically on startup.

### Backend

```powershell
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend: `http://127.0.0.1:5000`

### Frontend

Open a second terminal in the project root:

```powershell
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Optional SQL upgrade

If you prefer to prepare the database manually, `backend/schema_upgrade.sql` contains the new tables/columns. The current `app.py` also performs this upgrade automatically, so you normally do not need to import the file.

## Payment QR

Current file:

`public/payment-qr.png`

The supplied UPI QR image is already included and displayed on the payment page.

This project records the user's transaction/UTR ID. It does not automatically verify a bank/UPI transaction. Trustee verification is the confirmation step.
