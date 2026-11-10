# UML Design — Smart Parking Reservation System

## Use Case Diagram (PlantUML)
```plantuml
@startuml
left to right direction
actor Customer
actor Administrator as Admin
rectangle SmartPark {
 usecase "Register / Login" as UC1
 usecase "Browse Parking Lots" as UC2
 usecase "Check Slot Availability" as UC3
 usecase "Reserve Slot" as UC4
 usecase "View / Cancel Booking" as UC5
 usecase "Manage Parking Lots" as UC6
 usecase "Manage Parking Slots" as UC7
 usecase "View Bookings & Reports" as UC8
}
Customer --> UC1
Customer --> UC2
Customer --> UC3
Customer --> UC4
Customer --> UC5
Admin --> UC1
Admin --> UC6
Admin --> UC7
Admin --> UC8
@enduml
```

## Class Diagram (Mermaid)
```mermaid
classDiagram
class User {+id; +name; +email; +password_hash; +role}
class ParkingLot {+id; +name; +location; +hourly_rate; +active}
class ParkingSlot {+id; +lot_id; +slot_number; +slot_type; +active}
class Booking {+id; +booking_code; +user_id; +slot_id; +start_time; +end_time; +amount; +status}
class Payment {+id; +booking_id; +amount; +method; +status; +transaction_ref}
User "1" --> "0..*" Booking : creates
ParkingLot "1" --> "1..*" ParkingSlot : contains
ParkingSlot "1" --> "0..*" Booking : reserved in
Booking "1" --> "0..1" Payment : paid by
```

## Sequence Diagram — Reservation
```mermaid
sequenceDiagram
actor Customer
participant UI as Browser
participant App as Flask
participant DB as MySQL/SQLite
Customer->>UI: Select lot, slot and time
UI->>App: POST reservation
App->>DB: Check overlapping confirmed bookings
DB-->>App: Availability result
alt Available
 App->>DB: Insert booking and demo payment
 DB-->>App: Commit
 App-->>UI: Booking confirmation and reference
 UI-->>Customer: Show receipt
else Not available
 App-->>UI: Reject reservation
 UI-->>Customer: Choose another slot/time
end
```

## Activity Diagram — Booking
```mermaid
flowchart TD
A([Start]) --> B[Login]
B --> C[Browse parking lots]
C --> D[Select date and time]
D --> E[View available slots]
E --> F[Choose a slot]
F --> G{Slot still available?}
G -- No --> E
G -- Yes --> H[Enter vehicle number]
H --> I[Calculate amount]
I --> J[Create reservation and demo payment]
J --> K[Display booking reference]
K --> L([End])
```

## ER Diagram
```mermaid
erDiagram
USER ||--o{ BOOKING : creates
PARKING_LOT ||--|{ PARKING_SLOT : contains
PARKING_SLOT ||--o{ BOOKING : receives
BOOKING ||--o| PAYMENT : has
USER { int id PK; string name; string email UK; string password_hash; string role }
PARKING_LOT { int id PK; string name; string location; float hourly_rate }
PARKING_SLOT { int id PK; int lot_id FK; string slot_number; string slot_type; boolean active }
BOOKING { int id PK; string booking_code UK; int user_id FK; int slot_id FK; datetime start_time; datetime end_time; float amount; string status }
PAYMENT { int id PK; int booking_id FK; float amount; string method; string status; string transaction_ref UK }
```
