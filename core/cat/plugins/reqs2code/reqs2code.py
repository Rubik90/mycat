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

# Set the environment variable 'requirements2code_dir' to the directory where the plugin is located.
requirements2code_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['requirements2code_dir'] = requirements2code_dir

# Define directories for requirement and generated files
requirements_dir = os.path.join(requirements2code_dir, 'requirements')
generated_dir = os.path.join(requirements2code_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

# ENUM and Settings: Choose the target programming language for generated code.
class CodeLanguageSelect(Enum):
    PYTHON = 'Python'
    JAVA = 'Java'

class NLToCodeSettings(BaseModel):
    language: CodeLanguageSelect = CodeLanguageSelect.PYTHON

@plugin
def settings_schema():
    return NLToCodeSettings.model_json_schema()

def load_requirement_manual_from_excel(excel_file_path: str, req_id: str) -> Optional[str]:
    """
    Load the code manual content from the Excel file based on the REQ_ID.
    The Excel file is expected to have a column named 'CODE MANUAL'.
    """
    try:
        df = pd.read_excel(excel_file_path, sheet_name='Sheet1')
        row = df[df['REQ_ID'] == req_id]
        if row.empty:
            log.error(f"Requirement {req_id} not found in the Excel sheet.")
            return None

        content = row['CODE MANUAL'].values[0]
        if pd.isna(content) or not content.strip():
            log.error(f"Code Manual for {req_id} is empty or missing.")
            return None

        return content.strip()

    except FileNotFoundError:
        log.error(f"Excel file not found: {excel_file_path}")
    except Exception as e:
        log.error(f"Error reading Excel file {excel_file_path}: {e}")
    return None

def learn_excel_to_code(excel_file: str, requirements_dir: str) -> Optional[List[Dict]]:
    """
    Collect rows from the Excel file that contain software requirements and their associated code manual.
    Expected Excel columns: REQ_ID, REQUIREMENT, DETAILS, CODE MANUAL.
    """
    excel_path = os.path.join(requirements2code_dir, excel_file)
    try:
        df = pd.read_excel(excel_path)
        code_specifications = []

        for _, row in df.iterrows():
            req_id = str(row['REQ_ID']).replace("\n", " ")
            req_text = str(row['REQUIREMENT']).replace("\n", " ")
            details_text = str(row['DETAILS']).replace("\n", " ")

            code_manual = load_requirement_manual_from_excel(excel_path, req_id)
            if not code_manual:
                log.warning(f"No associated code manual found for REQ_ID: {req_id}")
                continue

            example = {
                'req_id': req_id,
                'requirement': req_text,
                'details': details_text,
                'code_manual': code_manual
            }
            code_specifications.append(example)

        return code_specifications
    except FileNotFoundError:
        log.error(f"Excel file {excel_file} not found in {requirements2code_dir}")
        return None
    except Exception as e:
        log.error(f"Error during reading of Excel file {excel_file}: {e}")
        return None

def save_generated_code_to_excel(code_outputs: List[str], req_id: str) -> None:
    """
    Save multiple generated code outputs under a single requirement ID
    in the Excel file (in a column named 'CODE MODEL').
    """
    try:
        excel_file = "in_out.xlsx"
        excel_path = os.path.join(requirements2code_dir, excel_file)
        df = pd.read_excel(excel_path, sheet_name='Sheet1')

        # Parse and combine code outputs (each parsed output is cleaned of extra commentary)
        parsed_codes = [parser(code) for code in code_outputs]
        combined_code = "\n\n".join(pc for pc in parsed_codes if pc).strip()

        # Find the row with the given req_id in the 'REQ_ID' column
        row_index = df[df['REQ_ID'] == req_id].index
        if row_index.empty:
            log.error(f"Requirement ID {req_id} not found in the Excel sheet.")
            return

        # Insert 'CODE MODEL' column next to 'CODE MANUAL' if needed
        if 'CODE MODEL' not in df.columns:
            code_manual_index = df.columns.get_loc('CODE MANUAL')
            df.insert(code_manual_index + 1, 'CODE MODEL', "")

        df.at[row_index[0], 'CODE MODEL'] = combined_code
        df.to_excel(excel_path, sheet_name='Sheet1', index=False)

        log.info(f"Generated code for {req_id} saved successfully in the Excel file.")
    except FileNotFoundError:
        log.error(f"Excel file {excel_file} not found in {requirements2code_dir}")
    except Exception as e:
        log.error(f"Error saving generated code to Excel file {excel_file}: {e}")

def invoke_llm_to_learn(examples: List[Dict], cat) -> None:
    """
    Invoke the LLM to 'learn' from the provided examples (training mode).
    No output is collected—this simply demonstrates how the model can be trained.
    """
    prompt = """
You are given a table with the following columns:
1. REQ_ID
2. REQUIREMENT
3. DETAILS
4. CODE MANUAL

Each row contains one software requirement along with a code manual. This is for training.
"""
    try:
        for i, example in enumerate(examples, 1):
            prompt += f"\nEXAMPLE {i}:\nREQ_ID: {example['req_id']}\nCODE MANUAL: {example['code_manual']}\n"

        cat.llm(prompt)
    except Exception as e:
        log.error(f"Error while invoking LLM to learn: {e}")

def train_nl_to_code(excel_file_name: str, cat) -> str:
    """Train the system with data from the given Excel file."""
    try:
        training_data = learn_excel_to_code(excel_file_name, requirements_dir)
        if training_data is None:
            return "Failed to read training data from Excel file."

        examples = []
        for data in training_data:
            examples.append({
                "input": (
                    f"REQ_ID: {data['req_id']}\n"
                    f"REQUIREMENT: {data['requirement']}\n"
                    f"DETAILS: {data['details']}\n"
                ),
                "output": data['code_manual']
            })
        invoke_llm_to_learn(examples, cat)

        return "Training completed successfully."
    except Exception as e:
        log.error(f"Error during training with the Excel file: {e}")
        return "An error occurred during the training."

def do_convert_nl_to_code(excel_file_name: str, cat) -> str:
    """
    Convert software requirements from Excel into generated code.
    Reads from 'REQ_ID', 'REQUIREMENT', and 'DETAILS' columns.
    """
    try:
        excel_path = os.path.join(requirements2code_dir, excel_file_name)
        df = pd.read_excel(excel_path)
        if df.empty:
            log.error("The Excel file is empty.")
            return "Conversion failed."

        code_outputs_by_req = {}

        # Get target language from settings (default is Python)
        settings = NLToCodeSettings()
        language = settings.language.value

        for _, row in df.iterrows():
            req_id = str(row['REQ_ID']).strip()
            requirement = str(row['REQUIREMENT']).strip()
            details = str(row['DETAILS']).strip()

            # Construct the prompt for code generation.
            prompt = f"""
You have these fields:
1. REQ_ID = {req_id}
2. REQUIREMENT = {requirement}
3. DETAILS = {details}

Please generate a code scaffold in {language} that implements this requirement.
Output only valid {language} code with no extra commentary or markdown formatting.
For example, for Python, include functions, classes, or a main block as needed.

Now do it:
"""
            llm_response = cat.llm(prompt)

            if llm_response:
                code_outputs_by_req.setdefault(req_id, []).append(llm_response)
            else:
                log.error(f"LLM failed to generate code for REQ_ID: {req_id}")

        # Save each requirement’s generated code back into the Excel file.
        for req_id, codes in code_outputs_by_req.items():
            save_generated_code_to_excel(codes, req_id)

        return "Conversion completed successfully."
    except Exception as e:
        log.error(f"Error during reading/conversion: {e}")
        return "Conversion failed."

def parser(generated_code: str) -> str:
    """
    Processes the raw LLM output to extract clean code.
    If the output is wrapped in markdown code fences, these are removed.
    """
    # Remove markdown code fences if present
    code_block = re.search(r"```(?:\w+)?\n([\s\S]+?)\n```", generated_code)
    if code_block:
        return code_block.group(1).strip()
    return generated_code.strip()

@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Dict:
    """
    Provide a quick interface for:
    - req2code train
    - req2code convert

    Command examples:
    - "req2code train"
    - "req2code convert"
    """
    return_direct = False
    user_message = cat.working_memory["user_message_json"]["text"]
    excel_filename = "in_out.xlsx"

    if user_message.startswith("req2code"):
        _, *args = user_message.split(maxsplit=1)
        if args:
            if args[0] == "list":
                return {"output": "Listing is not implemented yet."}

            if args[0].startswith("convert"):
                response = do_convert_nl_to_code(excel_filename, cat)
                return {"output": response}

            if args[0].startswith("train"):
                response = train_nl_to_code(excel_filename, cat)
                return {"output": response}

        else:
            response = (
                "How to train the system to convert NL to code:\n"
                "Type: req2code train\n"
                "How to convert the Excel file:\n"
                "Type: req2code convert"
            )
            return_direct = True

    if return_direct:
        return {"output": response}

    return fast_reply
