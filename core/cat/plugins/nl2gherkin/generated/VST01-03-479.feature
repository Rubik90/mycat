Here is the generated Gherkin scenario:

Feature: VST01-03-479
Scenario Outline: VST01-03-406
Given the unit is in POST-RUN
And the calibratable timer tShutdownZc1TimeoutThresh is exceeded
And NNetworkManagerStatusZc1 is not equal to NWK_MGR_STANDBY
When NEcuUpReasonZc1 is not equal to 0
Then ZC1 status becomes RUN
And a DTC is raised