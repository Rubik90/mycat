# Guide to Converting Test Cases into Gherkin Syntax
This guide will help you learn how to convert test cases written in natural language into Gherkin syntax. You will see examples composed of INPUT and the expected OUTPUT in Gherkin format.

## Input Structure
The INPUT is composed of the following fields:
* SDS (Feature ID): This should be written as is next to "Feature:".
* STC (Scenario ID): This should be written as is next to "Scenario:"/"Scenario Outline:", unless you find an OR condition in the input. If you find an OR condition, you have to write multiple "Scenario"/"Scenario Outline". For example, if you find "if J=A||B", you need to create a scenario where "J=A" and another where "J=B". Note that the OR condition can be expressed in various ways: "||", "OR", "|", "OR". When writing multiple scenarios, each should have the same Scenario ID plus "_n", where 'n' is an incremental value. 
* Procedure: This is the procedure to follow to do the test. Use this field to write the "Given" and "When" statements. This field could also contain:
    * Precodition: The initial state before the main test steps are executed. Use this to write the "Given" section.
    * Test Steps: The actions to perform during the test. Use this to write the "When" section.
* Pass Criteria: The conditions to determine whether the test has been passed or not. Use this field to write the "Then" statement.
* Description: The test description. It provides additional context or clarification for understanding the "Procedure" and "Pass Criteria".

## Output Structure
The OUTPUT should be structured as follows. Text in round brackets are notes, and text in square brackets relates to fields from the INPUT.
```
Feature: [sds]
    Scenario Outline: [stc] (or [stc]_n)
        Given ... (if needed)
        And ... (if needed)
        When ... 
        And ... (if needed)
        Then ...
        And ... (if needed)
        Examples: 
        | Placeholder1          |   Placeholder2        | ...
        | Variable1a/Value1a    |   Variable2a/Value2a  | ...
        | Variable1b/Value1b    |   Variable2b/Value2b  | ...
```

## Transformation Steps
1) Read the "SDS" field to give a value to "Feature".
2) Read the whole input to:
    - Get a general idea of what the test is about.
    - Determine how many OR conditions are present in the input and based on this, determine how many scenarios need to be generated.
3) Read "STC" and, based on step 2, name the scenarios.
4) Read the Procedure field. If it has a Precondition, use it to write the Given statement and its And statements. Otherwise, skip to step 6.
5) If the Procedure field has Test Steps, use it to write the When statement and its And statements. Otherwise, skip to step 6.
6) If you haven't already written Given and When, read the Procedure field and write the Given and When statements and their And statements.
7) Read the Pass Criteria field and use it to write the Then statement.
8) Read the Description field and ensure the Gherkin output matches it.
9) Finally:
    1) Read the entire output.
    2) Check that it complies with Gherkin syntax. If not, review and fix it.
    3) Remove any comments from the output, if present.

## Choosing Between Scenario and Scenario Outline
**Scenario Outline** allows you to add an "Examples" table at the end of the Gherkin test. The table consists of two or more rows:
- The first row contains placeholders that are present in the Gherkin code.
- The rows after the first have a value or a variable name that substitutes the corresponding placeholder during the tests.
When there is a variable like a threshold, a timer value, or any other similar value, you should use a Scenario Outline.

## Examples
Now I am going to give you all the examples. You will see something like this:
```
EXAMPLE #example_incremental_number
INPUT:
    ...here the content...
OUTPUT:
    ...here the content...
```

### EXAMPLE 1.
#### INPUT:
* SDS: COM01-02-879
* STC: COM01-02-3941
* Procedure: NNetworksResponseValidZc1(bit3) = True && Quick response time elapsed && NFaultUnlatchRequestMCU = 0x0 latch && neMotorROutboard is received
* Pass Criteria: Diag Window MCU = Enabled
* Description: Diagnostic Window shall be activated for MCU when: 
    - Hybrid_CAN Network status is active 
    - EDSU Fault Unlatching Mechanism is not requested (please refer to SDS ENM01-07 req [2300]) 
    - Quick Network communication response time has elapsed (Wake Up MCU + debounce time) 
    - Messages received from MCU
#### OUTPUT:
```
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
```

### EXAMPLE 2
#### INPUT:
* SDS: VST01-03-479
* STC: VST01-03-406
* Procedure: 
    - Precondition: ZC1 is in POST-RUN and within a calibratable timer 
    - Test Steps: tShutdownZc1TimeoutThresh the network management does not report that all the networks are in shutdown (NNetworkManagerStatusZc1 != NWK_MGR_STANDBY_NNetworkManagerStatus). 
* Pass Criteria: Verify: the ZC1 transition back in RUN mode ZC1 raises a DTC 
* Description: ZC1 ASW shall transition to RUN if any of the up reasons become active whilst in POST RUN.
#### OUTPUT:
```
    Feature: VST01-03-479
        Scenario Outline: VST01-03-406
            Given ZC1 ASW is in POST RUN
            When within a calibratable <timer> the network management does not report that all the networks are in shutdown
            Then ZC1 ASW is in RUN MODE
            And ZC1 ASW raises a <DTC>
            Examples: 
            | timer                      | DTC |
            | tShutdownZc1TimeoutThresh  | TBD |
```

### EXAMPLE 3
#### INPUT:
* SDS: VST01-01-482
* STC: VST01-01-460
* Procedure: 
    1. Set NIgnitionStatus = 2 
    2. Change door status, NDoorLOpenStatus changes value || NDoorROpenStatus changes value (possible values are Open and Closed).
* Pass Criteria: Reset IgnSt2Timeout Timer
* Description: The Timer IgnSt2Timeout shall reset if either of the doors are either opened or closed.
#### OUTPUT:
```
    Feature: VST01-01-482
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
```

### EXAMPLE 4
#### INPUT:
* SDS: ENM01-04-371
* STC: ENM01-04-349
* Procedure: 
    - Precondition: NHybridStatus = "Standby" 
    - Test Steps: NHybridStatus = 0x8 "ChrgStarting" for a calibratable time period AND (minSOC_BMS increasing OR IOBCHV > Threshold(HSU_Cal)) AND NIPUOBCStatus == (0x1 "Normal" OR "Derate")
* Pass Criteria: NHybridStatus = 0x9 "HybridOBC"
* Description: Once the EDSU is in 'Charge Starting' state AND charge exit conditions are not met [380], the EDSU shall transition to 'Charging' state if EDSU confirms charging is in progress from positive charging current. The EDSU shall stay in 'Charge Starting' state for a minimum calibratable time period before transition to 'Charging' state if charge exit conditions are not met [380]. Appropriate debounce and filtering mechanism shall apply to SoC increase and positive charging current confirmation.
#### OUTPUT:
```
    Feature: ENM01-04-371
        Scenario Outline: ENM01-04-349_1
            Given NHybridStatus is Standby
            When NHybridStatus is set to ChrgStarting for a <calibratable> time period
            And minSOC_BMS increasing
            And NIPUOBCStatus is Normal
            Then NHybridStatus is HybridOBC
            Examples: 
            | calibratable |
            | 1            |
            | 2            |

        Scenario Outline: ENM01-04-349_2
            Given NHybridStatus is Standby
            When NHybridStatus is set to ChrgStarting for a <calibratable> time period
            And IOBCHV > <HSU_Cal>
            And NIPUOBCStatus is Normal
            Then NHybridStatus is HybridOBC
            Examples: 
            | calibratable | HSU_Cal |
            | 1            | 1       |
            | 2            | 2       |

        Scenario Outline: ENM01-04-349_3
            Given NHybridStatus is Standby
            When NHybridStatus is set to ChrgStarting for a <calibratable> time period
            And minSOC_BMS increasing
            And NIPUOBCStatus is Derate
            Then NHybridStatus is HybridOBC
            Examples: 
            | calibratable |
            | 1            |
            | 2            |

        Scenario Outline: ENM01-04-349_4
            Given NHybridStatus is Standby
            When NHybridStatus is set to ChrgStarting for a <calibratable> time period
            And IOBCHV > <HSU_Cal>
            And NIPUOBCStatus is Derate
            Then NHybridStatus is HybridOBC
            Examples: 
            | calibratable | HSU_Cal |
            | 1            | 1       |
            | 2            | 2       |
```

### EXAMPLE 5
#### INPUT:
* SDS: PWT03-181
* STC: PWT03-231
* Procedure: 
    - Precondition: 
        1. Go to Ignition 5 
        2. Engine Running 
        3. Brake Pressed 
    - Test Steps: 
        1. Generate an Overboost condition (pBoost > Threshold, 2.5Bar)
* Pass Criteria: Verify that PID04_CalculatedLoad <= 80% during that ignition cycle
* Description: While the engine is running, if at any time there is an overboost condition (pBoost > Pressure Threshold) then the air charge in the engine shall be limited to 80% (PID04_CalculatedLoad <= 80%) for the remainder of the ignition cycle
#### OUTPUT:
```
    Feature: PWT03-181
        Scenario Outline: PWT03-231
            Given Ignition Status is 5
            And Engine is running
            And Brake pedal is pressed
            When Boost Pressure > <pBoost_threshold> bar
            Then Air charge is limited to <load_limit> in percentage
            Examples: 
            | pBoost_threshold | load_limit |
            | 2.5              | 80         |
```

### EXAMPLE 6
#### INPUT:
* SDS: PWT07-188
* STC: PWT07-246 PWT07-477
* Procedure: 
    - 246: 
        - Preconditions: 
        1) VehState.INIgnitionStatus = 5; 
        2) The Engine is on (nEngine > 0); 
        3) No DTC to be logged on ECM. 
        - Test Steps: 
        1) Set Head Coolant Temp Sensor (I_A_CTS1) > 108 degC; 
        2) Check the Pass Criteria 1); 
        3) Set B_KL15 = 0 (achieved going to Ignition 3); 
        4) Keep Head Coolant Temp Sensor (I_A_CTS1) > 108 degC; 
        5) Set Set B_KL15 = 1 (achieved going to Ignition 5) in 320s from B_KL15 = 0; 
        6) Check the Pass Criteria 2). 
    - 477: 
        - Preconditions: NIgnitionStatus = 0
        - Test Steps: NIgnitionStatus = 5 || TCoolant < 98.5 Deg || After Run Timer = 320 seconds
- Pass Criteria: 
    - 246: 
        1) 
            - Cooling_Fan_Relay_Low_Side_Low_Speed_ (O_S_FAN1) = Off (12V);
            - Cooling_Fan_Relay_Low_Side_High_Speed_ (O_S_FAN2) = On (0V). 
        2) 
            - Cooling_Fan_Relay_Low_Side_Low_Speed_ (O_S_FAN1) = Off (12V);
            - Cooling_Fan_Relay_Low_Side_High_Speed_ (O_S_FAN2) = Off (12V).
    - 477: rFan1ECM = 0% 
- Description: The HTR fans shall no longer be requested if the Ignition is switched back on and the engine Coolant head temperature falls below a threshold or the afterrun timer expires
#### OUTPUT:
```
    Feature: PWT07-188
        Scenario: PWT07-246_1
            Given Ignition Status is 5
            And Engine is on
            And No DTC are logged on ECM
            When Head Coolant Temp Sensor (I_A_CTS1) > 108 degC
            Then HTR fan is requested to be ON
            And LTR fan is requested to be OFF

        Scenario: PWT07-246_2
            Given Ignition Status is set to 3
            And Head Coolant Temp Sensor (I_A_CTS1) > 108 degC
            When Ignition Status is set to 5
            And Wait 320 s
            Then HTR fan is requested to be OFF
            And LTR fan is requested to be OFF

        Scenario: PWT07-477
            Given Ignition Status is set to 0
            When Ignition Status is set to 5
            And Head Coolant Temp Sensor (I_A_CTS1) < 98.5 degC
            Then HTR fan is requested to be OFF
```

### EXAMPLE 7
#### INPUT:
- SDS: HMI01-143
- STC: HMI01-214
- Procedure: 
    1. Set NIgnitionStatus>=5 
    2. Activate High beam, i.e. NFlassMainSwitch = 0x1 or 0x2 & NHBABodyStatus != ON
- Pass Criteria: High Beam tell-tale Illuminated
- Description: If NHBABodyStatus != ON && NFlashMainSwitch == "0x1 - Momentary flash" or "0x2 - Main beam toggle", the High Beam tell-tale SHALL be illuminated.
#### OUTPUT:
```
    Feature: HMI01-143
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
```

### EXAMPLE 8
#### INPUT:
- SDS: CHS05-2288
- STC: CHS05-1234 
- Procedure: (NAPMUModeEngaged = 2 (Sport) || 3 (Track)) && NignitionStatus transition from IS < 3 to IS >= 5
- Pass Criteria: NAPMUModeEngaged = 14 (Transition), NAPMUModeChangeReq = 0 (Normal), NAPMUModeChangeStatus = Available, Within 20 seconds: NAPMUModeEngaged = 0 (Normal)
- Description: When the selected handling mode is Sport or Track and there is an ignition cycle, the suspension mode change shall be initialised and transition to the default handling mode (Comfort).
#### OUTPUT:
```
    Feature: CHS05-2288
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
```