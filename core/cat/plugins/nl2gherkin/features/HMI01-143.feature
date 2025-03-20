Feature: HMI01-143
If NHBABodyStatus != ON  &&
NFlashMainSwitch == “0x1 – Momentary flash” or “0x2 – Main beam toggle”, the High Beam tell-tale SHALL be illuminated.

  Scenario: HMI01-214_1
    Given NIgnitionStatus = 5
    When NFlashMainSwitch = 0x1
    And NHBABodyStatus != ON
    Then High Beam tell-tale is Illuminated

  Scenario: HMI01-214_2
    Given NIgnitionStatus = 5
    When NFlashMainSwitch = 0x2
    And NHBABodyStatus != ON
    Then High Beam tell-tale is Illuminated