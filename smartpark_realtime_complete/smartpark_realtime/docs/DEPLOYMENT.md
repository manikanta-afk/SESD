# Deployment Notes

## Render + MySQL
1. Push repository to GitHub.
2. Create a reachable MySQL database with schema/database `smart_parking`.
3. Create a Render Blueprint from `render.yaml`.
4. Set `DATABASE_URL` to `mysql+pymysql://user:password@host:3306/smart_parking` (URL-encode special characters in credentials).
5. Set `ADMIN_PASSWORD` to a strong unique password and keep the generated `SECRET_KEY` private.
6. Deploy and test registration, booking, cancellation and admin dashboard.

The hosting service must be able to reach the MySQL host. Use a managed database or a provider that permits inbound connections from the hosting service. Keep credentials in hosting environment variables, never in source control.

## Security before public use
Enable HTTPS; change the demo admin password; use a strong SECRET_KEY; add CSRF protection (for example Flask-WTF), rate limiting, email verification, database backups, structured logging and database locking for concurrent reservations. Configure trusted proxy/secure cookie settings for the chosen host. Demo payment must not be represented as a real payment gateway.
