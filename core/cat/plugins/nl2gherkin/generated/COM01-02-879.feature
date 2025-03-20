Feature: COM01-02-879

Scenario Outline: COM01-02-3941
Given NNetworksResponseValidZc1(bit3) = True
And Quick response time elapsed
And NFaultUnlatchRequestMCU = 0x0 latch
And neMotorROutboard is received
Then Diag Window MCU = Enabled

Examples:
|  |  |  |  |
| NNetworksResponseValidZc1(bit3) = True | Quick response time elapsed | NFaultUnlatchRequestMCU = 0x0 latch | neMotorROutboard is received |
| true | true | 0x0 | received |