Feature: VST01-01-482
The Timer IgnSt2Timeout shall reset if either of the doors are either opened or closed.

  Scenario: VST01-01-460_1
    Given NIgnitionStatus is 2
    And NDoorLOpenStatus is Closed
    And NDoorROpenStatus is Closed
    When NDoorLOpenStatus is Open
    Then IgnSt2Timeout Timer is resetted

  Scenario: VST01-01-460_2
    Given NIgnitionStatus is 2
    And NDoorLOpenStatus is Closed
    And NDoorROpenStatus is Closed
    When NDoorROpenStatus is Open
    Then IgnSt2Timeout Timer is resetted

  Scenario: VST01-01-460_3
    Given NIgnitionStatus is 2
    And NDoorLOpenStatus is Open
    And NDoorROpenStatus is Open
    When NDoorLOpenStatus is Closed
    Then IgnSt2Timeout Timer is resetted

  Scenario: VST01-01-460_4
    Given NIgnitionStatus is 2
    And NDoorLOpenStatus is Open
    And NDoorROpenStatus is Open
    When NDoorROpenStatus is Closed
    Then IgnSt2Timeout Timer is resetted