Feature: CHS05-2288
When the selected handling mode is Sport or Track and there is an ignition cycle, the suspension mode change shall be initialised and transition to the default handling mode (Comfort).

  Scenario: CHS05-1234_1
    Given NAPMUModeEngaged = 2
    And NignitionStatus = 2
    When NignitionStatus = 5
    Then NAPMUModeEngaged = 14 during Ignition transition
    And NAPMUModeChangeReq = 0
    And NAPMUModeChangeStatus = Available
    And NAPMUModeEngaged = 0 within 20s from Ignition transition

  Scenario: CHS05-1234_2
    Given NAPMUModeEngaged = 3
    And NignitionStatus = 2
    When NignitionStatus = 5
    Then NAPMUModeEngaged = 14 during Ignition transition
    And NAPMUModeChangeReq = 0
    And NAPMUModeChangeStatus = Available
    And NAPMUModeEngaged = 0 within 20s from Ignition transition