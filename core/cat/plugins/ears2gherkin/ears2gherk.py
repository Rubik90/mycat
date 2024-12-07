from cat.mad_hatter.decorators import tool, hook, plugin
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import os
from cat.log import log

# Define directories for feature and generated files
ears2gherkin_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['ears2gherkin_dir'] = ears2gherkin_dir

# Create a directory for generated Gherkin files if it doesn't exist
generated_dir = os.path.join(ears2gherkin_dir, 'generated')
os.makedirs(generated_dir, exist_ok=True)

# Define Settings for the plugin
class EARS2GherkinSettings(BaseModel):
    language: str = "English"

@plugin
def settings_schema():
    return EARS2GherkinSettings.schema()

# Function to load EARS content from an Excel file
def load_ears_data_from_excel(excel_file_path: str) -> Optional[pd.DataFrame]:
    """Load EARS content from the Excel file."""
    try:
        return pd.read_excel(excel_file_path)
    except FileNotFoundError:
        log.error(f"Excel file not found: {excel_file_path}")
    except Exception as e:
        log.error(f"Error reading Excel file {excel_file_path}: {e}")
    return None

# Function to translate EARS to Gherkin
def translate_ears_to_gherkin(ears: str, system: str, natural: str) -> str:
    """
    Translate EARS format into Gherkin syntax.
    Args:
        ears: The EARS format string.
        system: The system or feature name.
        natural: The natural language description of the requirement.

    Returns:
        A Gherkin-formatted string.
    """
    try:
        # Simplistic transformation logic based on EARS patterns
        lines = []
        lines.append(f"Feature: {system.strip()}")
        lines.append(f"Scenario: {natural.strip()}")
        
        # Parse EARS for When, Given, and Then patterns
        if "when" in ears.lower():
            lines.append(f"Given {ears.split(',')[0].strip().capitalize()}")
            lines.append(f"When {ears.split(',')[1].split('shall')[0].strip()}")
            lines.append(f"Then {ears.split('shall')[-1].strip()}")

        return "\n".join(lines)
    except Exception as e:
        log.error(f"Error while translating EARS to Gherkin: {e}")
        return "Translation failed"

# Function to perform translation on all rows in the Excel
def translate_ears_excel_to_gherkin(excel_file: str) -> Optional[List[str]]:
    """
    Read EARS data from an Excel file and translate it to Gherkin syntax.

    Args:
        excel_file: Path to the Excel file containing EARS data.

    Returns:
        A list of Gherkin scenarios as strings.
    """
    excel_path = os.path.join(ears2gherkin_dir, excel_file)
    data = load_ears_data_from_excel(excel_path)
    if data is None:
        return None

    gherkin_scenarios = []
    for _, row in data.iterrows():
        try:
            system = str(row.get("SYS", "")).strip()
            natural = str(row.get("Natural", "")).strip()
            ears = str(row.get("EARS", "")).strip()
            gherkin = translate_ears_to_gherkin(ears, system, natural)
            gherkin_scenarios.append(gherkin)
        except Exception as e:
            log.warning(f"Error processing row: {e}")
            continue
    return gherkin_scenarios

# Save Gherkin scenarios back to an Excel file
def save_gherkin_to_excel(scenarios: List[str], excel_file: str):
    """
    Save Gherkin scenarios to an Excel file.

    Args:
        scenarios: List of Gherkin scenarios.
        excel_file: Path to the output Excel file.
    """
    try:
        output_path = os.path.join(generated_dir, excel_file)
        pd.DataFrame({"Gherkin Scenarios": scenarios}).to_excel(output_path, index=False)
        log.info(f"Gherkin scenarios saved to {output_path}")
    except Exception as e:
        log.error(f"Error saving Gherkin scenarios to Excel: {e}")

# Tool to initiate the EARS-to-Gherkin conversion
@tool
def ears_to_gherkin(tool_input, cat):
    """Convert EARS requirements in an Excel file to Gherkin syntax."""
    try:
        # If tool_input is a string, treat it as the file path
        if isinstance(tool_input, str):
            excel_file = tool_input
        elif isinstance(tool_input, dict):
            excel_file = tool_input.get("excel_file")
        else:
            return "Invalid input format. Provide an Excel file path or a dictionary with 'excel_file'."

        if not excel_file:
            return "Please provide an Excel file containing EARS requirements."

        gherkin_scenarios = translate_ears_excel_to_gherkin(excel_file)
        if not gherkin_scenarios:
            return "Conversion failed or no valid data found in the Excel file."

        save_gherkin_to_excel(gherkin_scenarios, f"gherkin_{os.path.basename(excel_file)}")
        return "EARS to Gherkin conversion completed successfully."
    except Exception as e:
        log.error(f"Error during EARS to Gherkin conversion: {e}")
        return f"An error occurred during the conversion: {e}"

# Hook for customizing responses
@hook(priority=0)
def ears2gherkin_hook(message, cat):
    """Custom hook to rephrase responses or handle special commands."""
    user_message = message["content"]
    if user_message.startswith("ears2g"):
        response = {
            "train": "Training is not supported for EARS-to-Gherkin.",
            "convert": (
                "To convert EARS to Gherkin, type: 'ears2g convert excel-file.xlsx'. "
                "Ensure the Excel file contains SYS, Natural, and EARS columns."
            ),
        }.get(user_message.split()[1], "Unsupported EARS2Gherkin command.")
        message["content"] = response
    return message
