Feature: PWT07-188
The HTR fans shall no longer be requested if the Ignition is switched back on and the engine Coolant head temperature falls below a threshold or the afterrun timer expires

  Scenario: PWT07-246_1
    Given Ignition Status is 5
    And Engine is on
    And No DTC are logged on ECM
    When Head Coolant Temp Sensor (I_A_CTS1) > 108 degC
    Then HTR fan is requested to be ON

  Scenario: PWT07-246_2
    Given Ignition Status is set to 3
    And Head Coolant Temp Sensor (I_A_CTS1) > 108 degC
    When Ignition Status is set to 5
    And Wait 320 s
    Then HTR fan is requested to be OFF

  Scenario: PWT07-477
    Given Ignition Status is set to 0
    When Ignition Status is set to 5
    And Head Coolant Temp Sensor (I_A_CTS1) < 98.5 degC
    Then HTR fan is requested to be OFF