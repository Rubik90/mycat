Here is the generated Gherkin scenario:

Feature: ENM01-05-697

Scenario Outline: ENM01-05-437
Given VehState_PDU.NIgnitionStatus = 2
And wait for 60 seconds, observe NIgnitionStatus = 1
When Simulate State of Charge < LV SOC Low threshold and wait for 60 minutes
Then BwarrantedUVP is set to 0x1

Examples:
|  |
| BLVSOCCheckTimer = 0x01 &&
BUVPFlag = 1 &&
LISB_SOC_Relative <= LV_SOC_Pre_UVP |