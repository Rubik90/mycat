Feature: COM01-02-879

  Scenario Outline: COM01-02-3941
    When <Hybrid_CAN Network status> is active
    And <EDSU Fault Unlatching Mechanism> is not requested
    And <Quick Network communication response time> has elapsed
    And <Messages received> from MCU
    Then the <Diagnostic Window> is enabled
    Examples: 
      | Hybrid_CAN Network status       | EDSU Fault Unlatching Mechanism | Quick Network communication response time | Messages received | Diagnostic Window |
      | NNetworksResponseValidZc1(bit3) | NFaultUnlatchRequestMCU         | Quick response time elapsed               | neMotorROutboard  | Diag Window MCU   |
      | True 				| False 			  | 100 			              | isvalid 	  | True 	      |