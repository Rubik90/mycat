Feature: VST01-03-479

  Scenario Outline: VST01-03-406
    Given ZC1 ASW is in POST RUN
    When within a calibratable <timer> the network management does not report that all the networks are in shutdown
    Then ZC1 ASW is in RUN MODE
    And ZC1 ASW raises a <DTC>
    Examples: 
      | timer                      | DTC |
      | tShutdownZc1TimeoutThresh  | TBD |