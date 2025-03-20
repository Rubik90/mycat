Here is the generated Gherkin scenario:

Feature: ENM01-04-378
Scenario Outline: ENM01-04-353
Precondition:
Given Ethernet.NHybridFault is not 3 "Level 2 Fault"
And Ethernet.NIginitionStatus is either 3 or 5
When HV.NIPUVehicletethered is 2 "Tethered_communicated" # HV battery charging
Then Hybrid.minSOC_BMS increases
And Hybrid.chargeState_BMS is 1 "CHARGESTATE_COMPLETE"

Examples:
| Ethernet.NHybridFault | Ethernet.NIginitionStatus |
| Not 3 "Level 2 Fault"   | 3 or 5                  |

When Ethernet.NHybridStatus is 0xA "Charge Complete"
Then Ethernet.NIPUCommand will not be 1 "OBC Disabled"