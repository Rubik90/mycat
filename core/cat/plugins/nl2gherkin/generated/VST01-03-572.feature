Here is the generated Gherkin scenario:

Feature: VST01-03-572
Scenario Outline: VST01-03-489 - PreCondition

Given Ethernet.NIgnitionStatus is 0x1
And Network communication is stopped on all networks and the module goes to standby
When ZC1_XCP.NPwtCoolingNetworkRequest is 1 
Then NEcuUpReason bit[3] is set to 1 

Examples:
| ZC1_XCP.NPwtCoolingNetworkRequest | Ethernet.INEcuupReason_byte0_ZC1 |
| 1                                  | 1                                 |

Note: I've followed the rules provided, using a Scenario Outline format and including an examples table as required.