import os
import pandas as pd
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from cat.mad_hatter.decorators import tool, hook, plugin
from cat.log import log

# Set the environment variable ‘nl2gherkin_dir’ to the directory where the plugin is located.
nl2gherkin_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['nl2gherkin_dir'] = nl2gherkin_dir

# Define directories for feature and generated files
features_dir = os.path.join(nl2gherkin_dir, 'features')
generated_dir = os.path.join(nl2gherkin_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

# Settings
class LanguageSelect(Enum):
    EN = 'English'
    IT = 'Italian'

class NLToGherkinSettings(BaseModel):
    Language: LanguageSelect = LanguageSelect.EN

@plugin
def settings_schema():
    return NLToGherkinSettings.schema()

import pandas as pd
from typing import Optional

def load_excel_file(excel_path: str) -> Optional[pd.DataFrame]:
    """Load and validate Excel file"""
    try:
        if not os.path.exists(excel_path):
            log.error(f"Excel file not found: {excel_path}")
            return None
            
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        if df.empty:
            log.error("Excel file is empty")
            return None
            
        return df
    except Exception as e:
        log.error(f"Error reading Excel file {excel_path}: {e}")
        return None

def load_feature_file_from_excel(excel_file_path: str, file_id: str) -> Optional[str]:
    """Load the Gherkin Manual content from the Excel file"""
    df = load_excel_file(excel_file_path)
    if df is None:
        return None
        
    try:
        row = df[df['SDS'] == file_id]
        if row.empty:
            log.error(f"Feature file {file_id} not found in the Excel sheet")
            return None
        
        content = row['Gherkin_Manual'].values[0]
        if pd.isna(content) or not content.strip():
            log.error(f"Gherkin Manual for {file_id} is empty or missing")
            return None
        
        return content.strip()
    except Exception as e:
        log.error(f"Error processing row for {file_id}: {e}")
        return None

def learn_excel_to_gherkin(excel_file: str, feature_files_dir: str) -> Optional[List[Dict]]:
    """Process Excel file and extract Gherkin specifications"""
    excel_path = os.path.join(nl2gherkin_dir, excel_file)
    df = load_excel_file(excel_path)
    if df is None:
        return None
    
    try:
        gherkin_specifications = []
        required_columns = ['SDS', 'STC', 'Procedure', 'Pass criteria', 'Description']
        
        for column in required_columns:
            if column not in df.columns:
                log.error(f"Required column '{column}' not found in Excel file")
                return None

        for _, row in df.iterrows():
            sds = str(row['SDS']).strip()
            feature_content = load_feature_file_from_excel(excel_path, sds)

            if not feature_content:
                log.warning(f"No associated feature file or Gherkin manual found for SDS: {sds}")
                continue

            example = {
                'sds': sds,
                'stc': str(row['STC']).strip(),
                'procedure': str(row.get('Procedure', '')).strip(),
                'pass_criteria': str(row.get('Pass criteria', 'Actuation')).strip(),
                'description': str(row.get('Description', 'Trigger')).strip(),
                'gherkin': feature_content
            }
            gherkin_specifications.append(example)

        return gherkin_specifications
    except Exception as e:
        log.error(f"Error processing Excel file: {e}")
        return None

def save_gherkin_scenario_to_excel(scenarios: List[str], feature_name: str) -> bool:
    """Save multiple Gherkin scenarios under a single feature to the 'Gherkin_Model' column of the Excel file."""
    if not scenarios or not feature_name:
        log.error("Invalid input: scenarios list or feature name is empty")
        return False

    try:
        excel_file = "example.xlsx"
        excel_path = os.path.join(nl2gherkin_dir, excel_file)
        
        df = load_excel_file(excel_path)
        if df is None:
            return False
        
        # Parse and combine scenarios into a single string
        parsed_scenarios = [parser(scenario) for scenario in scenarios if scenario]
        if not parsed_scenarios:
            log.error("No valid scenarios to save")
            return False
            
        combined_scenarios = "\n\n".join(parsed_scenarios)

        # Find the row with the given feature_name in the 'SDS' column
        row_index = df[df['SDS'] == feature_name].index
        if row_index.empty:
            log.error(f"Feature name {feature_name} not found in the Excel sheet")
            return False
        
        # Add 'Gherkin_Model' column if it doesn't exist
        if 'Gherkin_Model' not in df.columns:
            df['Gherkin_Model'] = ""
        
        # Update the 'Gherkin_Model' column for the found row
        df.at[row_index[0], 'Gherkin_Model'] = combined_scenarios
        
        # Save the updated DataFrame back to the Excel file
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)
        
        log.info(f"Gherkin scenarios for {feature_name} saved successfully in the Excel file")
        return True
    except Exception as e:
        log.error(f"Error saving Gherkin scenarios to Excel file {excel_file}: {e}")
        return False
    
def invoke_llm_to_learn(examples: List[Dict], cat) -> None:
    """Invoke the LLM to learn from provided data."""
    if not examples:
        log.warning("No examples provided for training")
        return

    try:
        # Validate examples structure and content
        for example in examples:
            if not all(key in example for key in ['input', 'output']):
                log.error("Invalid example structure: missing required fields")
                return
            if not example['input'] or not example['output']:
                log.error("Invalid example content: empty input or output")
                return
            if not isinstance(example['input'], str) or not isinstance(example['output'], str):
                log.error("Invalid example type: input and output must be strings")
                return
    except Exception as e:
        log.error(f"Error while validationg examples structure and content {e}")

        prompt = """
Guide to Converting Test Cases into Gherkin Syntax
This guide will help you learn how to convert test cases written in natural language into Gherkin syntax. You will see examples composed of INPUT and the expected OUTPUT in Gherkin format.

Input Structure
The INPUT is composed of the following fields:
- SDS (Feature ID): This should be written as is next to "Feature:".
- STC (Scenario ID): This should be written as is next to "Scenario:"/"Scenario Outline:", unless you find an OR condition in the input. If you find an OR condition, you have to write multiple "Scenario"/"Scenario Outline". For example, if you find "if J=A||B", you need to create a scenario where "J=A" and another where "J=B". Note that the OR condition can be expressed in various ways: "||", "OR", "|", "OR". When writing multiple scenarios, each should have the same Scenario ID plus "_n", where 'n' is an incremental value. 
- Procedure: This is the procedure to follow to do the test. Use this field to write the "Given" and "When" statements. This field could also contain:
    - Precodition: The initial state before the main test steps are executed. Use this to write the "Given" section.
    - Test Steps: The actions to perform during the test. Use this to write the "When" section.
- Pass Criteria: The conditions to determine whether the test has been passed or not. Use this field to write the "Then" statement.
- Description: The test description. It provides additional context or clarification for understanding the "Procedure" and "Pass Criteria".

Output Structure
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

Transformation Steps
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

Choosing Between Scenario and Scenario Outline
Scenario Outline allows you to add an "Examples" table at the end of the Gherkin test. The table consists of two or more rows:
- The first row contains placeholders that are present in the Gherkin code.
- The rows after the first have a value or a variable name that substitutes the corresponding placeholder during the tests.
When there is a variable like a threshold, a timer value, or any other similar value, you should use a Scenario Outline.

Examples
Now I am going to give you all the examples. You will see something like this:
```
EXAMPLE #example_incremental_number
INPUT:
    ...here the content...
OUTPUT:
    ...here the content...
```
"""

    try:
        i = 1
        for example in examples:
            prompt += f"""EXAMPLE {i}
                          INPUT:{example['input']}
                          OUTPUT:{example['output']}
"""
            i += 1

        cat.llm(prompt)
        # log.info(f"Training prompt:\n{prompt}")

    except Exception as e:
        log.error(f"Error while invoking LLM to learn: {e}")

def train_nl_to_gherkin(excel_file_name: str, cat) -> str:
    """Train the system with examples from the given Excel file."""
    try:
        training_data = learn_excel_to_gherkin(excel_file_name, features_dir)
        if training_data is None:
            return "Failed to read training data from Excel file."

        examples = []
        for data in training_data:
            if data['gherkin'] != "No associated feature file found":
                examples.append({
                    "input": (f"SDS: {data['sds']}\nSTC: {data['stc']}\nProcedure: {data['procedure']}\n"
                              f"Pass criteria: {data['pass_criteria']}\nDescription: {data['description']}\n"),
                    "output": data['gherkin']
                })
        invoke_llm_to_learn(examples, cat)

        return "Training completed successfully"
    except Exception as e:
        log.error(f"Error during training with the Excel file: {e}")
        return "An error occurred during the training"

def do_convert_nl_to_gherkin(excel_file_name: str, cat) -> str:
    """Perform the conversion from NL to Gherkin using the trained LLM."""
    try:
        df = pd.read_excel(os.path.join(nl2gherkin_dir, excel_file_name))
        if df.empty:
            log.error("The Excel file is empty")
            return "Conversion failed"

        gherkin_scenarios_by_feature = {}

        for _, row in df.iterrows():
            sds = str(row['SDS']).replace("\n", "")
            stc = str(row['STC']).replace("\n", "")
            procedure = str(row.get('Procedure', ''))#.replace("\n", "")
            pass_criteria = str(row.get('Pass criteria', 'Actuation'))#.replace("\n", "")
            description = str(row.get('Description', 'Trigger'))#.replace("\n", "")

            llm_input = (
                f"SDS: {sds}\n"
                f"STC: {stc}\n"
                f"Procedure: {procedure}\n"
                f"Pass criteria: {pass_criteria}\n"
                f"Description: {description}\n"
            )
            
            prompt = f"""
This guide details how to convert natural language test cases into Gherkin syntax, illustrating the transformation from INPUT to the expected OUTPUT in Gherkin format.

Input Structure
1) SDS (Feature ID): Directly maps to the "Feature:" in Gherkin.
2) STC (Scenario ID): Maps to "Scenario:" or "Scenario Outline:".
3) Procedure:
    - Precondition: Translates to "Given".
    - Test Steps: Translates to "When".
4) Pass Criteria: Translates to "Then".
5) Description: Provides context for understanding the Procedure and Pass Criteria.

Output Structure
The OUTPUT in Gherkin shall follow this structure:
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

Transformation Steps
1) Feature: Use the "SDS" field.
2) Scenario Count: Identify OR conditions to determine the number of scenarios.
3) Scenario Naming: Name scenarios using "STC" and, if needed, add suffixes based on OR conditions.
4) OR handling: When you find OR conditions (e.g., "if J=A||B"), create multiple scenarios, each with the same Scenario ID suffixed by "_n".
5) Given: Use the Procedure's Precondition.
6) When: Use the Procedure's Test Steps.
7) Then: Use the Pass Criteria.
8) Validation: Ensure the Gherkin output aligns with the Description.
9) Review:
    1) Read the entire output.
    2) Ensure compliance with Gherkin syntax.
    3) Remove any comments.

Choosing Between Scenario and Scenario Outline
- Scenario Outline: Use when there are variables such as thresholds or timers.
- Examples Table: Includes placeholders and corresponding values or variables.

Please, pay attention to the following things:
- Do not use any markup in the output that you produce
- Do not add any note at the top like "Here is the converted test case..." or at the end like "Note: I've followed the guidelines ...". We want a pure gherkin output.

Convert the following test case into Gherkin syntax, adhering to examples you saw before and the rules above:
INPUT: {llm_input}
"""
            llm_response = cat.llm(prompt)


            if llm_response:
                if sds not in gherkin_scenarios_by_feature:
                    gherkin_scenarios_by_feature[sds] = []
                gherkin_scenarios_by_feature[sds].append(llm_response)
            else:
                log.error(f"LLM failed to generate Gherkin for SDS: {sds}")

        # Update xlsx and save inference output in .xlsx files
        for sds, scenarios in gherkin_scenarios_by_feature.items():
            save_gherkin_scenario_to_excel(scenarios, sds)


        return "Conversion completed successfully"
    except Exception as e:
        log.error(f"Error during reading the Excel file: {e}")
        return "Conversion failed"

def parser(scenario: str) -> Optional[str]:
    """Parse a Gherkin scenario to ensure proper formatting."""
    if not scenario or not isinstance(scenario, str):
        log.warning("Invalid scenario input: empty or not a string")
        return None
        
    try:
        # Remove extra whitespace and normalize line endings
        parsed = scenario.strip().replace('\r\n', '\n').replace('\r', '\n')
        
        # Basic validation of Gherkin structure
        if not any(keyword in parsed.lower() for keyword in ['feature:', 'scenario:', 'given', 'when', 'then']):
            log.warning("Scenario appears to be missing required Gherkin keywords")
            return None
            
        return parsed
    except Exception as e:
        log.error(f"Error parsing scenario: {e}")
        return None
        
@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Dict:
    """Handle fast replies from the agent."""
    return_direct = False
    user_message = cat.working_memory["user_message_json"]["text"]
    #excel_filename = "240617_SDS_STC_Gherkin.xlsx"
    excel_filename = "example.xlsx"

    if user_message.startswith("nl2g"):
        _, *args = user_message.split(maxsplit=1)
        if args:
            if args[0] == "list":
                return {"output": "Listing is not implemented yet"}

            if args[0].startswith("convert"):
                # _, *subargs = args[0].split(maxsplit=1)
                # if subargs:
                # excel_filename = subargs[0]
                response = do_convert_nl_to_gherkin(excel_filename, cat)
                return {"output": response}
                # else:
                #     return {"output": "Please, provide an Excel file to convert: nl2gherkin convert excel-file.xlsx"}

            if args[0].startswith("train"):
                # _, *subargs = args[0].split(maxsplit=1)
                # if subargs:
                # excel_filename = subargs[0]
                response = train_nl_to_gherkin(excel_filename, cat)
                return {"output": response}
                # else:
                #     return {"output": "Please, provide an Excel file to train: nl2gherkin train excel-file.xlsx"}

        else:
            response = ("How to train the cat to convert NL to gherkin:"
                        "\nType: nl2g train"
                        "\nHow to convert a .xlsx file:"
                        "\nType: nl2g convert")
            return_direct = True

    if return_direct:
        return {"output": response}

    return fast_reply


