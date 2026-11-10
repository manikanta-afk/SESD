# SmartPark database schema

The project uses SQLAlchemy models and creates tables automatically. The included SQLite file is a pre-initialized starter database; the app can also create an empty database and seed it with `flask --app app init-db`.

## Tables
- `user`: customer/admin accounts, email, password hash, role, registration timestamp.
- `parking_lot`: parking facility metadata and hourly rate.
- `parking_slot`: individual numbered spaces belonging to a facility.
- `booking`: customer, slot, time window, vehicle registration, amount and status.

## Relationship summary
`user 1—many booking`; `parking_lot 1—many parking_slot`; `parking_slot 1—many booking`.

Passwords are stored as Werkzeug password hashes. Do not store plaintext passwords. The starter database contains only the demo administrator, parking locations and slots; customer records are created when people register.
