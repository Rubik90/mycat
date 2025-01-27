import os
import re
import pandas as pd
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from cat.log import log
from cat.mad_hatter.decorators import hook, plugin
from cat.looking_glass.cheshire_cat import CheshireCat

cat = CheshireCat()

# Set the environment variable ‘ears2gherkin_dir’ to the directory where the plugin is located.
ears2gherkin_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['ears2gherkin_dir'] = ears2gherkin_dir

# Define directories for feature and generated files
features_dir = os.path.join(ears2gherkin_dir, 'features')
generated_dir = os.path.join(ears2gherkin_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

# ENUM and Settings
class LanguageSelect(Enum):
    EN = 'English'
    IT = 'Italian'

class NLToGherkinSettings(BaseModel):
    Language: LanguageSelect = LanguageSelect.EN

@plugin
def settings_schema():
    return NLToGherkinSettings.model_json_schema()

def load_feature_file_from_excel(excel_file_path: str, file_id: str) -> Optional[str]:
    """Load the Gherkin Manual content from the Excel file based on the SYS field."""
    try:
        df = pd.read_excel(excel_file_path, sheet_name='Sheet1')
        row = df[df['SYS'] == file_id]
        if row.empty:
            log.error(f"Feature file {file_id} not found in the Excel sheet.")
            return None

        content = row['GHERKIN MANUAL'].values[0]
        if pd.isna(content) or not content.strip():
            log.error(f"Gherkin Manual for {file_id} is empty or missing.")
            return None

        return content.strip()

    except FileNotFoundError:
        log.error(f"Excel file not found: {excel_file_path}")
    except Exception as e:
        log.error(f"Error reading Excel file {excel_file_path}: {e}")
    return None

def learn_excel_to_gherkin(excel_file: str, feature_files_dir: str) -> Optional[List[Dict]]:
    """Collect rows from the Excel file that contain EARS data and Gherkin manual."""
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
        log.error(f"Error during reading of Excel file {excel_file}: {e}")
        return None

def save_gherkin_scenario_to_excel(scenarios: List[str], feature_name: str) -> None:
    """
    Save multiple Gherkin outputs under a single feature name
    in the Excel file (in 'GHERKIN MODEL').
    """
    try:
        excel_file = "in_out.xlsx"
        excel_path = os.path.join(ears2gherkin_dir, excel_file)
        df = pd.read_excel(excel_path, sheet_name='Sheet1')

        # Combine scenarios
        parsed_scenarios = [parser(scenario) for scenario in scenarios]
        # Join them with a blank line in between
        combined_scenarios = "\n\n".join(ps for ps in parsed_scenarios if ps).strip()

        # Find the row with the given feature_name in the 'SYS' column
        row_index = df[df['SYS'] == feature_name].index
        if row_index.empty:
            log.error(f"Feature name {feature_name} not found in the Excel sheet.")
            return

        # Insert 'GHERKIN MODEL' column next to 'GHERKIN MANUAL' if needed
        if 'GHERKIN MODEL' not in df.columns:
            gherkin_manual_index = df.columns.get_loc('GHERKIN MANUAL')
            df.insert(gherkin_manual_index + 1, 'GHERKIN MODEL', "")

        df.at[row_index[0], 'GHERKIN MODEL'] = combined_scenarios
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)

        log.info(f"Gherkin scenarios for {feature_name} saved successfully in the Excel file.")
    except FileNotFoundError:
        log.error(f"Excel file {excel_file} not found in {ears2gherkin_dir}")
    except Exception as e:
        log.error(f"Error saving Gherkin scenarios to Excel file {excel_file}: {e}")

def invoke_llm_to_learn(examples: List[Dict], cat) -> None:
    """
    Invoke the LLM to 'learn' from provided data (training mode).
    No output is collected here—just demonstration to the model.
    """
    prompt = """
You are given a table with the following columns:
1. SYS
2. EARS
3. NATURAL
4. GHERKIN MANUAL

Each row contains one requirement. This is just for training.
"""
    try:
        for i, example in enumerate(examples, 1):
            prompt += f"\nEXAMPLE {i}:\nSYS: {example['input']}\nGHERKIN: {example['output']}\n"

        cat.llm(prompt)
    except Exception as e:
        log.error(f"Error while invoking LLM to learn: {e}")

def train_nl_to_gherkin(excel_file_name: str, cat) -> str:
    """Train the system with data from the given Excel file."""
    try:
        training_data = learn_excel_to_gherkin(excel_file_name, features_dir)
        if training_data is None:
            return "Failed to read training data from Excel file."

        examples = []
        for data in training_data:
            if data['gherkin'] != "No associated feature file found":
                examples.append({
                    "input": (
                        f"SYS: {data['sys']}\n"
                        f"EARS: {data['ears']}\n"
                        f"NATURAL: {data['natural']}\n"
                    ),
                    "output": data['gherkin']
                })
        invoke_llm_to_learn(examples, cat)

        return "Training completed successfully."
    except Exception as e:
        log.error(f"Error during training with the Excel file: {e}")
        return "An error occurred during the training."

def do_convert_nl_to_gherkin(excel_file_name: str, cat) -> str:
    """
    Convert EARS requirements to Gherkin steps including a 'Feature' line
    and minimal Gherkin steps (Given/When/Then).
    Reads from 'SYS', 'EARS', and 'NATURAL' columns in the Excel file.
    """
    try:
        df = pd.read_excel(os.path.join(ears2gherkin_dir, excel_file_name))
        if df.empty:
            log.error("The Excel file is empty.")
            return "Conversion failed."

        gherkin_scenarios_by_feature = {}

        for _, row in df.iterrows():
            sys_val = str(row['SYS']).strip()
            ears_val = str(row['EARS']).strip()
            natural_val = str(row['NATURAL']).strip()

            # Prompt: produce exactly four lines
            prompt = f"""
You have these fields:
1. SYS = {sys_val}
2. EARS = {ears_val}
3. NATURAL = {natural_val} (ignore entirely)

Please produce exactly four lines in this order:
1) Feature: {sys_val}
2) Given [transformation of the WHERE clause]
3) When [transformation of the WHEN clause]
4) Then [transformation of the THEN clause]

No extra commentary or lines. No blank lines before or after. 
Ignore NATURAL completely.

Example:
SYS: ShoppingCart
EARS: WHERE cart is empty WHEN user adds item THEN system SHALL increase count

Desired Output (exactly four lines):
Feature: ShoppingCart
Given cart is empty
When user adds item
Then system SHALL increase count

Now do it:
"""

            llm_input = prompt
            llm_response = cat.llm(llm_input)

            if llm_response:
                # Collect the raw LLM response for this feature
                gherkin_scenarios_by_feature.setdefault(sys_val, []).append(llm_response)
            else:
                log.error(f"LLM failed to generate Gherkin for SYS: {sys_val}")

        # Save each feature’s generated Gherkin to the Excel file
        for feature_name, scenarios in gherkin_scenarios_by_feature.items():
            save_gherkin_scenario_to_excel(scenarios, feature_name)

        return "Conversion completed successfully."
    except Exception as e:
        log.error(f"Error during reading/conversion: {e}")
        return "Conversion failed."

def parser(combined_scenario: str) -> str:
    """
    Ensures the final result has exactly four lines in this order:
    1) Feature: ...
    2) Given ...
    3) When ...
    4) Then ...
    Skips duplicates, chain-of-thought, or anything else.
    """

    # We'll store each of the four lines separately if we find them
    feature_line = None
    given_line = None
    when_line = None
    then_line = None

    # Split by lines
    lines = combined_scenario.splitlines()

    for line in lines:
        stripped = line.strip()

        # Skip blank lines or any commentary
        if not stripped:
            continue

        # Match the lines we want, in order
        if feature_line is None and stripped.startswith("Feature:"):
            feature_line = stripped
            continue

        # Next, see if we still need a Given line
        if given_line is None and re.match(r'^Given\b', stripped):
            given_line = stripped
            continue

        # Next, the When line
        if when_line is None and re.match(r'^When\b', stripped):
            when_line = stripped
            continue

        # Finally, the Then line
        if then_line is None and re.match(r'^Then\b', stripped):
            then_line = stripped
            continue

        # If we've filled all 4, we can break early
        if feature_line and given_line and when_line and then_line:
            break

    # Build the final output lines (only if they're not None)
    final_lines = []
    if feature_line:
        final_lines.append(feature_line)
    if given_line:
        final_lines.append(given_line)
    if when_line:
        final_lines.append(when_line)
    if then_line:
        final_lines.append(then_line)

    return "\n".join(final_lines).strip()

@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Dict:
    """
    Provide a quick interface for:
    - ears2g train
    - ears2g convert
    """
    return_direct = False
    user_message = cat.working_memory["user_message_json"]["text"]
    excel_filename = "in_out.xlsx"

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
            response = (
                "How to train the cat to convert NL to Gherkin:\n"
                "Type: ears2g train\n"
                "How to convert a .xlsx file:\n"
                "Type: ears2g convert"
            )
            return_direct = True

    if return_direct:
        return {"output": response}

    return fast_reply
