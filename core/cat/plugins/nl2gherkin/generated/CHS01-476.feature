Feature: CHS01-476
Scenario Outline: On wake up, system provides pump speed based on vehicle speed
Given NEPHSStatus is 0x1
And NIgnitionStatus has transitioned from 0x0 or 0x1 to a higher value
And vVehicleESP equals 655.35
When vehicle speed matches 'vehicleSpeedinit' in the referenced map
Then NEPHSMotor matches the corresponding pump speed for 'vehicleSpeedinit'
Examples:
  | vehicleSpeedinit |
  | 100 |
  | 200 |
  | 300 |