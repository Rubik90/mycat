Here is the generated Gherkin scenario:

Feature: HMI01-143

Scenario Outline: HMI01-214
Given NIgnitionStatus is greater than or equal to 5
And NFlashMainSwitch is either "0x1" or "0x2"
And NHBABodyStatus is not "ON"
When the conditions are met
Then High Beam tell-tale is illuminated

Examples:
| NFlashMainSwitch | NHBABodyStatus |
| "0x1 - Momentary flash" | "OFF" |
| "0x2 - Main beam toggle" | "OFF" |