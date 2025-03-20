Feature: PWT03-181
Scenario Outline: PWT03-231
Given the engine is running
And the brake is pressed
And ignition is set to 5
When pBoost exceeds the pressure threshold
Then PID04_CalculatedLoad is limited to 80%
Examples:
| pBoost | Pressure Threshold |
| >2.5Bar | 2.5Bar |
