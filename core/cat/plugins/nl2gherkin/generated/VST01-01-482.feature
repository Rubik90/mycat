Here is the generated Gherkin scenario:

Feature: VST01-01-482
Scenario Outline: VST01-01-460

Given NIgnitionStatus is 2
And either NDoorLOpenStatus changes value or NDoorROpenStatus changes value
When IgnSt2Timeout Timer is triggered
Then the IgnSt2Timeout Timer resets

Examples:
| NIgnitionStatus | NDoorLOpenStatus | NDoorROpenStatus |
| 2              | changed          | not changed     |
| 2              | not changed     | changed         |
| 2              | changed         | changed         |