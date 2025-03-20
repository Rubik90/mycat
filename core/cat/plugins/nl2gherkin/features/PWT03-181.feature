Feature: PWT03-181
While the engine is running, if at any time there is an overboost condition (pBoost > Pressure Threshold) then the air charge in the engine shall be limited to 80% (PID04_CalculatedLoad <= 80%) for the remainder of the ignition cycle

  Scenario Outline: PWT03-231
    Given Ignition Status is 5
    And Engine is running
    And Brake pedal is pressed
    When Boost Pressure > <pBoost_threshold> bar
    Then Air charge is limited to <load_limit> in percentage
    Examples: 
      | pBoost_threshold | load_limit |
      | 2.5              | 80         |