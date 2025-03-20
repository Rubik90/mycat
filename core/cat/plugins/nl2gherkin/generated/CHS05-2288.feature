Here is the generated Gherkin scenario:

Feature: CHS05-2288
Scenario Outline: CHS05-1234
Given NAPMUModeEngaged is 2 or 3
And NignitionStatus is less than 3
When NignitionStatus transitions to 5 or greater
Then NAPMUModeEngaged should be 14 within 20 seconds
And NAPMUModeChangeReq should be 0 within 20 seconds
And NAPMUModeChangeStatus should be Available within 20 seconds

Examples:
| NAPMUModeEngaged | NignitionStatus |
| 2 (Sport)        | <3               |
| 3 (Track)        | <3               |