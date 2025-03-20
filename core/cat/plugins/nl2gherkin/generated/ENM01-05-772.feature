Here is the generated Gherkin scenario:

Feature: ENM01-05-772

Scenario Outline: ENM01-05-489
Given PDCDCHVMax > threshold HSU_CAL
And NIPUDCDCStatus == 0x1 Normal || 0x3 Derate
And ST_DCSW_HVSTO == 0x2 Closed
And NHybridFault != 0x3 (Level 2)
When BHVOKtoCharge = 1

Examples:
| PDCDCHVMax | NIPUDCDCStatus | ST_DCSW_HVSTO | NHybridFault |
| > threshold HSU_CAL | 0x1 Normal || 0x3 Derate | 0x2 Closed | != 0x3 (Level 2) |