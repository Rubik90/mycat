Feature: PWT07-188

Scenario Outline: PWT07-246/477
Given VehState.INIgnitionStatus is Ignition (5)
And The Engine is on (nEngine > 0)
And No DTC to be logged on ECM
When Head Coolant Temp Sensor (I_A_CTS1) is set greater than 108 degC
Then Pass criteria 1
When B_KL15 is set to 0 (Accessory)
And Keep Head Coolant Temp Sensor (I_A_CTS1) greater than 108 degC
Then Set B_KL15 to 1 (Ignition without cranking) in 320s from B_KL15 = 0
And Check the Pass criteria 2

Examples:
| VehState.INIgnitionStatus | The Engine | No DTC on ECM |
| Ignition (5)              | On          | False         |

Scenario Outline: PWT07-246/477
Given NIgnitionStatus is 0
When NIgnitionStatus is equal to 5 or TCoolant is less than 98.5 Deg or After Run Timer is equal to 320 seconds
Then Pass criteria:
  | Condition                         |
  | Cooling_Fan_Relay_Low_Side_Low_Speed_ (O_S_FAN1) = Off (12V), Cooling_Fan_Relay_Low_Side_High_Speed_ (O_S_FAN2) = On (0V)    |
  | Cooling_Fan_Relay_Low_Side_Low_Speed_ (O_S_FAN1) = Off (12V), Cooling_Fan_Relay_Low_Side_High_Speed_ (O_S_FAN2) = Off (12V) |

Examples:
| NIgnitionStatus | TCoolant | After Run Timer |
| 0               |          | 320             |