Feature: VST01-01-693
Scenario Outline: VST01-01-N Scenari
Given the Ignition State is 2
And the door is either open or closed inside or outside the vehicle
And the LV Battery State of Charge is not 'Pre-UVP'
And the Ethernet Status and ADI are stable and communicating
When an Authorized key is detected inside or outside the vehicle
Then the Ignition State shall transition to State 3

Examples: 
| door status | battery state | ethernet status | adi status |
| Open        | Not Pre-UVP    | Stable          | Communicating |
| Closed      | Not Pre-UVP    | Stable          | Communicating |
| Open        | Not Pre-UVP    | Unstable       | Non-communicating |
| Closed      | Pre-UVP        | Stable          | Communicating |