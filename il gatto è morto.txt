import os
from pydantic import BaseModel
from cat.log import log
import pandas as pd
from typing import Dict, List, Optional
from enum import Enum
from cat.mad_hatter.decorators import hook, plugin
from cat.log import log
from cat.looking_glass.cheshire_cat import CheshireCat

cat = CheshireCat

# Set the environment variable ‘ears2gherkin_dir’ to the directory where the plugin is located.
ears2gherkin_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['ears2gherkin_dir'] = ears2gherkin_dir

# Define directories for feature and generated files
features_dir = os.path.join(ears2gherkin_dir, 'features')
generated_dir = os.path.join(ears2gherkin_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

# Settings
class LanguageSelect(Enum):
    EN = 'English'
    IT = 'Italian'

class NLToGherkinSettings(BaseModel):
    Language: LanguageSelect = LanguageSelect.EN

@plugin
def settings_schema():
    return NLToGherkinSettings.model_json_schema()

def load_feature_file_from_excel(excel_file_path: str, file_id: str) -> Optional[str]:
    """Load the Gherkin Manual content from the Excel file"""
    try:
        # Load the Excel file
        df = pd.read_excel(excel_file_path, sheet_name='Sheet1')

        # Find the row with the given file_id in the 'SYS' column
        row = df[df['SYS'] == file_id]

        if row.empty:
            log.error(f"Feature file {file_id} not found in the Excel sheet")
            return None

        # Get the content from the 'GHERKIN MANUAL' column
        content = row['GHERKIN MANUAL'].values[0]

        if pd.isna(content) or not content.strip():
            log.error(f"Gherkin Manual for {file_id} is empty or missing")
            return None

        return content.strip()
    except FileNotFoundError:
        log.error(f"Excel file not found: {excel_file_path}")
    except Exception as e:
        log.error(f"Error reading Excel file {excel_file_path}: {e}")
    return None

def learn_excel_to_gherkin(excel_file: str, feature_files_dir: str) -> Optional[List[Dict]]:
    """Read the Excel file"""
    excel_path = os.path.join(ears2gherkin_dir, excel_file)

    try:
        df = pd.read_excel(excel_path)

        gherkin_specifications = []

        for _, row in df.iterrows():
            sys = str(row['SYS']).replace("\n", " ")
            feature_content = load_feature_file_from_excel(excel_path, sys)

            if not feature_content:
                log.warning(f"No associated feature file or Gherkin manual found for SYS: {sys}")
                continue

            example = {
                'sys': sys,
                'ears': str(row['EARS']).replace("\n", " "),
                'natural': str(row['NATURAL']).replace("\n", " "),
                'gherkin': feature_content
            }
            gherkin_specifications.append(example)

        return gherkin_specifications
    except FileNotFoundError:
        log.error(f"Excel file {excel_file} not found in {ears2gherkin_dir}")
        return None
    except Exception as e:
        log.error(f"Error during the reading of Excel file {excel_file}: {e}")
        return None

def save_gherkin_scenario_to_excel(scenarios: List[str], feature_name: str) -> None:
    """Save multiple Gherkin scenarios under a single feature to the 'GHERKIN MODEL' column of the Excel file."""
    try:
        excel_file = "in_out_few.xlsx"
        # Load the Excel file
        excel_path = os.path.join(ears2gherkin_dir, excel_file)
        df = pd.read_excel(excel_path, sheet_name='Sheet1')

        # Parse and combine scenarios into a single string
        parsed_scenarios = [parser(scenario) for scenario in scenarios]
        combined_scenarios = "\n\n".join(parsed_scenarios)

        # Find the row with the given feature_name in the 'SYS' column
        row_index = df[df['SYS'] == feature_name].index

        if row_index.empty:
            log.error(f"Feature name {feature_name} not found in the Excel sheet")
            return

        # Add the 'GHERKIN MODEL' column if it does not exist
        if 'GHERKIN MODEL' not in df.columns:
            # df['GHERKIN MODEL'] = ""  # Initialize the column with empty strings
            # Find the index of the 'GHERKIN MANUAL' column
            gherkin_manual_index = df.columns.get_loc('GHERKIN MANUAL')

            # Insert the 'GHERKIN MODEL' column to the right of 'GHERKIN MANUAL'
            df.insert(gherkin_manual_index + 1, 'GHERKIN MODEL', "")
        # Update the 'GHERKIN MODEL' column for the found row
        df.at[row_index[0], 'GHERKIN MODEL'] = combined_scenarios

        # Save the updated DataFrame back to the Excel file
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)

        log.info(f"Gherkin scenarios for {feature_name} saved successfully in the Excel file.")
    except FileNotFoundError:
        log.error(f"Excel file {excel_file} not found in {ears2gherkin_dir}")
    except Exception as e:
        log.error(f"Error saving Gherkin scenarios to Excel file {excel_file}: {e}")

def invoke_llm_to_learn(examples: List[Dict], cat) -> None:
    """Invoke the LLM to learn from provided data."""

    prompt = """
Guide to Converting EARS Requirements into Gherkin Syntax

This guide explains how to convert requirements written in EARS (Easy Approach to Requirements Syntax) into Gherkin syntax. You will learn the structure of EARS, common keywords, and how to map EARS patterns to Gherkin's `Given`, `When`, `Then` constructs.

EARS Structure

EARS requirements typically follow a structured format using keywords to define the context, trigger, and expected outcome of a system behavior. Common EARS keywords include:

-   `WHERE`: Defines a precondition or context.
-   `WHEN`: Specifies an event or trigger.
-   `IF`: Introduces a conditional event.
-   `THEN`: Describes the expected system response.
-   `SHALL`: Indicates a mandatory requirement.

EARS to Gherkin Mapping

The general approach to converting EARS to Gherkin involves:

1.  **Context (Given):**  Use `WHERE` clauses from EARS to establish the initial context in Gherkin's `Given` steps.
2.  **Trigger (When):** Translate `WHEN` or `IF` clauses into Gherkin's `When` steps, describing the event that initiates the system behavior.
3.  **Outcome (Then):** Map the `THEN` clause, along with the `SHALL` keyword indicating the expected response, to Gherkin's `Then` steps, outlining the desired outcome.

Input Structure

The INPUT is composed of the following fields:

-   `SYS` (Feature ID):  Write this as is next to "Feature:".
-   `EARS`: The requirement written in EARS syntax. Use this field to extract `Given`, `When`, `Then`.
-   `NATURAL`: A natural language description of the requirement. Use this field to ensure that the generated Gherkin matches the intended meaning.

Output Structure

The OUTPUT should be structured as follows:

Feature: [SYS]
Scenario: [A brief description of the scenario]
Given [Preconditions from WHERE clause]
When [Event or trigger from WHEN or IF clause]
Then [Expected system response from THEN clause, indicated by SHALL]
And [Additional outcome or constraint, if needed]


Transformation Steps

1.  Read the `SYS` field and write it after "Feature:".
2.  Read the `EARS` field:
    -   Identify `WHERE` clauses to define preconditions (`Given`).
    -   Identify `WHEN` or `IF` clauses to define the trigger event (`When`).
    -   Identify `THEN` clauses, along with `SHALL`, to define the expected system response (`Then`).
3.  Read the `NATURAL` field to ensure the generated Gherkin accurately reflects the requirement's intent.
4.  Write the Gherkin scenario, following the `Given-When-Then` structure.
5.  Review the output:
    -   Ensure it complies with Gherkin syntax.
    -   Remove any comments.

Examples

Now I am going to give you all the examples. You will see something like this:

EXAMPLE #example_incremental_number
INPUT:
...here the content...
OUTPUT:
...here the content...

"""

    try:
        i = 1
        for example in examples:
            prompt += f"""
                    EXAMPLE {i}
                    INPUT: {example['input']}
                    OUTPUT: {example['output']}
                    """
            i += 1

        cat.llm(prompt)

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
                    "input": (f"SYS: {data['sys']}\nEARS: {data['ears']}\nNATURAL: {data['natural']}\n"),
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
        df = pd.read_excel(os.path.join(ears2gherkin_dir, excel_file_name))
        if df.empty:
            log.error("The Excel file is empty")
            return "Conversion failed"

        gherkin_scenarios_by_feature = {}

        for _, row in df.iterrows():
            sys = str(row['SYS']).replace("\n", "")
            ears = str(row['EARS']).replace("\n", "")
            natural = str(row['NATURAL']).replace("\n", "")

            llm_input = (
                f"SYS: {sys}\n"
                f"EARS: {ears}\n"
                f"NATURAL: {natural}\n"
            )

            prompt = f"""
Convert EARS Requirements to Gherkin Scenarios

Your task is to convert requirements written in EARS (Easy Approach to Requirements Syntax) into Gherkin scenarios. Follow the guidelines you learned during training and adhere to the structure and examples provided.

Input Structure

-   `SYS` (Feature ID): Directly corresponds to the "Feature:" in Gherkin.
-   `EARS`: The requirement in EARS syntax. This will be your primary source for creating the `Given`, `When`, `Then` steps.
-   `NATURAL`: A natural language description of the requirement. Use this to validate that your Gherkin output accurately reflects the requirement's meaning.

Output Structure

The Gherkin scenario should follow this structure:

Feature: [SYS]
Scenario: [Brief description based on EARS]
Given [Preconditions from WHERE clause in EARS]
When [Event/trigger from WHEN or IF clause in EARS]
Then [Expected system response from THEN clause in EARS, indicated by SHALL]
And [Additional outcome/constraint, if necessary]


Conversion Steps

1.  **Feature:** Use the `SYS` field directly after "Feature:".
2.  **Scenario:** Create a brief description of the scenario based on the `EARS` requirement.
3.  **Given:** Translate `WHERE` clauses from the `EARS` input into `Given` steps, establishing the initial context.
4.  **When:** Convert `WHEN` or `IF` clauses into `When` steps, describing the trigger event.
5.  **Then:** Map `THEN` clauses, especially those containing `SHALL`, to `Then` steps, outlining the expected system response.
6.  **Validation:** Use the `NATURAL` field to ensure your Gherkin output aligns with the intended meaning of the requirement.
7.  **Review:**
    -   Ensure your output strictly adheres to Gherkin syntax.
    -   Remove any comments or extraneous text. Your output should only contain the Gherkin scenario.

Important Notes

-   **Do not add any conversational elements or markup** like "Here is the converted test case..." or "Note: I've followed the guidelines...". We want a pure Gherkin output.
-   **Focus on the EARS to Gherkin conversion rules you learned during training.**

Convert the following EARS requirement into a Gherkin scenario, strictly adhering to the rules and examples you have learned:

INPUT: {llm_input}"""
        

            llm_response = cat.llm(prompt)

            if llm_response:
                if sys not in gherkin_scenarios_by_feature:
                    gherkin_scenarios_by_feature[sys] = []
                gherkin_scenarios_by_feature[sys].append(llm_response)
            else:
                log.error(f"LLM failed to generate Gherkin for SYS: {sys}")

        # Update xlsx and save inference output in .xlsx files
        for sys, scenarios in gherkin_scenarios_by_feature.items():
            save_gherkin_scenario_to_excel(scenarios, sys)

        return "Conversion completed successfully"
    except Exception as e:
        log.error(f"Error during reading the Excel file: {e}")
        return "Conversion failed"

def parser(combined_scenario: str) -> str:
    feature_index = combined_scenario.find("Feature")
    if feature_index != -1:
        return combined_scenario[feature_index:]
    return combined_scenario

@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Dict:
    """Handle fast replies from the agent."""
    return_direct = False
    user_message = cat.working_memory["user_message_json"]["text"]
    excel_filename = "in_out_few.xlsx"

    if user_message.startswith("ears2g"):
        _, *args = user_message.split(maxsplit=1)
        if args:
            if args[0] == "list":
                return {"output": "Listing is not implemented yet"}

            if args[0].startswith("convert"):
                response = do_convert_nl_to_gherkin(excel_filename, cat)
                return {"output": response}

            if args[0].startswith("train"):
                response = train_nl_to_gherkin(excel_filename, cat)
                return {"output": response}

        else:
            response = ("How to train the cat to convert NL to gherkin:"
                        "\nType: ears2g train"
                        "\nHow to convert a .xlsx file:"
                        "\nType: ears2g convert")
            return_direct = True

    if return_direct:
        return {"output": response}

    return fast_reply