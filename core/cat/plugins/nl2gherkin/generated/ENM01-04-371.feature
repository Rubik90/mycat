Feature: ENM01-04-371
Scenario Outline:
Given NHybridStatus equals 0x8 "ChrgStarting" for a calibratable time period
And minSOC_BMS is increasing or IOBCHV is greater than Threshold(HSU_Cal)
And NIPUOBCStatus is either 0x1 "Normal" or "Derate"
When EDSU confirms charging is in progress from positive charging current
Then NHybridStatus becomes 0x9 "HybridOBC"

Examples:
| NHybridStatus | minSOC_BMS | IOBCHV | NIPUOBCStatus |
| 0x8 "ChrgStarting" | increasing | > Threshold(HSU_Cal) | 0x1 "Normal" or "Derate" |