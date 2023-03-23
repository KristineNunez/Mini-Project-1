# Mini-Project-1
Kristine Bernadette Q. Nunez<br>
CS 173 (Blockchain Technologies)

Contract (Ghostnet): KT1Mu46UTaamkBTYcNnSbmyWbaaDmBF8nuxB

## Additional Functions
### 1. change_ticket_cost<br>
Parameters: new_ticket_cost (mutez)<br>
Expected Behavior: Changes lottery's ticket cost<br>
Assertions:
  * Operator is the one changing the ticket cost
  * No tickets are sold yet

### 2. change_max_tickets
Parameters: new_max_tickets<br>
Expected Behavior: Changes lottery's maximum available tickets<br>
Assertions:
  * Operator is the one changing the maximum available tickets
  * No tickets are sold yet

## Modified Functions
### 1. __init__<br>
New Parameters: op (address)<br>
New Behavior: Operator can be specified using op parameter

### 2. buy_ticket<br>
New Parameters: num_tickets<br>
New Behavior:
  * Players can buy multiple tickets
  * If player requests more tickets than available, just give remaining tickets
