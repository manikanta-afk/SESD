# Software Requirements Specification (SRS)
## Smart Parking Reservation and Management System

### 1. Introduction
**Purpose:** Specify requirements for a browser-based parking reservation application that enables customers to discover parking facilities, inspect slot availability for a time window, reserve a slot and review reservations. Administrators maintain parking facilities and slots.

**Scope:** The system supports customer and administrator roles, facility and slot management, time-window reservations, demo payment records, booking cancellation and basic operational reporting. Physical sensors, automatic number-plate recognition, gate controllers and live payment processing are outside the prototype scope.

**Definitions:** Lot = parking facility; Slot = individual parking space; Booking = reservation of a slot for a start/end interval; Admin = privileged operator.

### 2. Overall Description
**User classes:** Customer (searches and books); Administrator (manages facilities, slots and monitors bookings).

**Operating environment:** Modern desktop/mobile browser; Python 3.10+; Flask; SQLAlchemy; SQLite for local demo or MySQL for hosted deployment.

**Constraints:** Internet connection required for hosted use. A booking must have a future start time and end time later than start. A slot cannot have overlapping confirmed reservations.

### 3. Functional Requirements
- FR-01: The system shall allow a visitor to register with name, email and password.
- FR-02: The system shall authenticate users and distinguish customer and administrator roles.
- FR-03: A customer shall browse active parking facilities and view location and hourly rate.
- FR-04: A customer shall request slot availability for a date and time interval.
- FR-05: A customer shall reserve an available slot and provide a vehicle registration number.
- FR-06: The system shall calculate the booking amount from duration and hourly rate.
- FR-07: The system shall generate a unique booking reference and demo payment record.
- FR-08: A customer shall view their booking history and booking details.
- FR-09: A customer or administrator shall cancel an eligible future confirmed booking.
- FR-10: An administrator shall add parking facilities and create batches of parking slots.
- FR-11: An administrator shall enable/disable slots and inspect recent reservations.
- FR-12: The system shall expose a JSON endpoint for slot availability.

### 4. Non-functional Requirements
- NFR-01 Usability: Main booking workflow shall be accessible through responsive browser pages.
- NFR-02 Security: Passwords shall be stored as salted hashes; privileged routes shall enforce administrator role.
- NFR-03 Integrity: The system shall reject overlapping confirmed bookings for the same slot.
- NFR-04 Maintainability: Models, routes, templates, static assets and tests shall be separated.
- NFR-05 Portability: The app shall support SQLite for local development and MySQL via a database URL.
- NFR-06 Performance: Typical prototype requests should complete within three seconds under light demonstration load.

### 5. External Interface Requirements
**User interface:** Home, registration, login, parking list, lot/slot selection, customer dashboard, booking receipt and admin dashboard.
**Software interface:** Flask/SQLAlchemy to relational database; browser communicates with Flask over HTTP; availability endpoint returns JSON.

### 6. Data Requirements
Entities: User, ParkingLot, ParkingSlot, Booking and Payment. User has many bookings; a lot contains many slots; a slot has many bookings over time; a booking has zero or one payment record.

### 7. Business Rules
- Only authenticated customers can create reservations.
- Only administrators can manage parking inventory.
- A booking interval must be valid and in the future at booking time.
- Two confirmed reservations for the same slot must not overlap.
- Demo payment is recorded as successful only as a simulation; it is not a real financial transaction.

### 8. Acceptance Criteria
- A visitor can register and log in.
- A customer can view facilities, select a time window and reserve an available slot.
- An overlapping reservation is rejected.
- A customer can view and cancel an eligible future reservation.
- An administrator can add a facility and slots and inspect booking summaries.
- Automated tests pass in the configured test environment.
