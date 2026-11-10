# Test Plan

| ID | Test | Expected result |
|---|---|---|
| TP01 | Load home page | HTTP 200 and active lots shown |
| TP02 | Register valid user | Account created |
| TP03 | Register duplicate email | Duplicate rejected |
| TP04 | Login valid credentials | Customer dashboard shown |
| TP05 | Login invalid credentials | Error shown; no session |
| TP06 | Customer opens admin route | Access denied/redirect |
| TP07 | Search lot availability | Slot availability returned |
| TP08 | Reserve available future slot | Booking and demo payment created |
| TP09 | Reserve overlapping slot | Request rejected |
| TP10 | Cancel future booking | Booking status becomes cancelled |
| TP11 | Add parking lot as admin | New lot persisted |
| TP12 | Add parking slots as admin | New slots persisted |

## Test execution
Run `pytest -q`. Manual acceptance testing should additionally cover the customer booking workflow and administrator inventory workflow in a browser.
