# SmartPark — real-time parking reservation website

A full-stack Flask application matching the supplied SmartPark dashboard preview. It includes customer accounts, a persistent SQL database, parking inventory, reservation conflict checks, booking receipts, an admin view, and browser polling for live availability.

## Features
- Dashboard styling closely follows the supplied demo preview (sidebar, KPI cards, slot grid, location list, booking activity and reservation modal).
- Customer registration and login. Passwords are stored as secure password hashes, never as plain text.
- SQLAlchemy database: SQLite for local development; PostgreSQL for hosted deployment.
- Three seeded parking locations with 20 slots each.
- Time-window reservations, vehicle registration, calculated price, booking reference and receipt.
- Live availability refresh every four seconds. Reservations made in one browser appear as unavailable in other logged-in browsers on their next refresh.
- PostgreSQL row locking during reservation creation to reduce double-booking races.
- Admin overview at `/admin`.

## Run on Windows
1. Install Python 3.10+.
2. Extract this ZIP and open PowerShell in the `smartpark_realtime` folder.
3. Create a virtual environment and install packages:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Initialize the database and sample parking lots:

```powershell
flask --app app init-db
```

5. Start the website:

```powershell
python app.py
```

6. Open `http://127.0.0.1:5000` and create a customer account.

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
python app.py
```

## Database and customer data
- By default, SQLite stores data in `smartpark.db` in Flask's instance directory. It persists across app restarts on your computer.
- For a hosted multi-user website, configure `DATABASE_URL` to a persistent PostgreSQL database. The included Render Blueprint provisions a database and connects it to the web service.
- User names, email addresses, password hashes, booking details, vehicle registration numbers and booking status are stored in SQL tables.
- Do not delete the database file if you need to retain local customer records. Back it up regularly.

## Admin account
The database initializer creates `admin@smartpark.local`. Set `ADMIN_PASSWORD` before the first `init-db` run. If omitted locally, the initial demo password is `Admin@12345`. Change it before any public deployment. Admin route: `/admin`.

## Real-time behaviour — important distinction
The browser requests current availability from the server every four seconds. Because every browser reads from the same database, a successful reservation becomes visible to other connected users on the next refresh. This is near-real-time polling, not WebSocket push. It does not detect physical vehicles or barriers: live hardware requires IoT sensors, a gateway and a separate integration. Payment is currently a clearly labelled demo flow; no real money is collected.

## Deploy to Render
1. Push the extracted project folder to a GitHub repository.
2. In Render, create a Blueprint and select that repository. Render reads `render.yaml` and provisions the web service and PostgreSQL database.
3. Set a strong `ADMIN_PASSWORD` in the service environment before the first deploy.
4. Deploy, then open `/login`, register a customer and test two separate browsers to verify that a booking updates availability.
5. Back up the database and rotate secrets before public use.

## Before public/production use
Add CSRF protection, rate limiting, email verification/password reset, privacy policy and consent, audit logs, automated backups, monitoring, database migrations, and a real payment provider. Have the booking flow security-reviewed. Do not use the seeded admin credentials publicly.
