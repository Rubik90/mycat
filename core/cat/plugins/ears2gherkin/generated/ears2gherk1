# Import necessary libraries and modules
from cat.mad_hatter.decorators import tool, hook, plugin  # Importing decorators for plugin system and tool hooks
from pydantic import BaseModel  # Pydantic for defining schema models
from typing import Dict, List, Optional  # Type hinting for function signatures
from datetime import datetime  # To handle datetime functions if needed
import pandas as pd  # pandas for working with Excel data
import os  # Standard library for file system operations
from cat.log import log  # Import logging utility for error handling

# Define directories for feature and generated files
ears2gherkin_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
os.environ['ears2gherkin_dir'] = ears2gherkin_dir  # Set the environment variable for directory

# Create a directory for generated Gherkin files if it doesn't exist
generated_dir = os.path.join(ears2gherkin_dir, 'generated')  # Define path for generated Gherkin files
os.makedirs(generated_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Define Settings for the plugin
class EARS2GherkinSettings(BaseModel):  # Pydantic model to define plugin settings
    language: str = "English"  # Default language setting

@plugin
def settings_schema():  # Plugin decorator for exposing schema for settings
    return EARS2GherkinSettings.schema()  # Return the schema of the settings model

# Function to load EARS content from an Excel file
def load_ears_data_from_excel(excel_file_path: str) -> Optional[pd.DataFrame]:
    """Load EARS content from the Excel file."""
    try:
        return pd.read_excel(excel_file_path)  # Load the Excel file into a pandas DataFrame
    except FileNotFoundError:
        log.error(f"Excel file not found: {excel_file_path}")  # Log error if file is not found
    except Exception as e:
        log.error(f"Error reading Excel file {excel_file_path}: {e}")  # Log any other error
    return None  # Return None if there is an error

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
        lines = []  # Initialize an empty list for the lines of Gherkin output
        lines.append(f"Feature: {system.strip()}")  # Add Feature heading with system name
        lines.append(f"Scenario: {natural.strip()}")  # Add Scenario heading with natural description
        
        # Parse EARS for When, Given, and Then patterns
        if "when" in ears.lower():  # Check if 'when' is in the EARS string
            # Split EARS at the first comma and treat the first part as the 'Given' condition
            lines.append(f"Given {ears.split(',')[0].strip().capitalize()}")  
            # Split EARS at 'shall' and treat the first part as the 'When' action
            lines.append(f"When {ears.split(',')[1].split('shall')[0].strip()}")
            # The part after 'shall' is treated as the 'Then' outcome
            lines.append(f"Then {ears.split('shall')[-1].strip()}")

        return "\n".join(lines)  # Join all lines into a single string with newlines
    except Exception as e:
        log.error(f"Error while translating EARS to Gherkin: {e}")  # Log error if translation fails
        return "Translation failed"  # Return a failure message

# Function to perform translation on all rows in the Excel
def translate_ears_excel_to_gherkin(excel_file: str) -> Optional[List[str]]:
    """
    Read EARS data from an Excel file and translate it to Gherkin syntax.

    Args:
        excel_file: Path to the Excel file containing EARS data.

    Returns:
        A list of Gherkin scenarios as strings.
    """
    excel_path = os.path.join(ears2gherkin_dir, excel_file)  # Get the full path of the input Excel file
    data = load_ears_data_from_excel(excel_path)  # Load the EARS data into a pandas DataFrame
    if data is None:  # If loading failed, return None
        return None

    gherkin_scenarios = []  # List to store generated Gherkin scenarios
    for _, row in data.iterrows():  # Iterate through each row in the DataFrame
        try:
            # Extract 'SYS', 'Natural', and 'EARS' columns from the row
            system = str(row.get("SYS", "")).strip()
            natural = str(row.get("Natural", "")).strip()
            ears = str(row.get("EARS", "")).strip()
            # Translate the EARS format to Gherkin and add to the scenarios list
            gherkin = translate_ears_to_gherkin(ears, system, natural)
            gherkin_scenarios.append(gherkin)
        except Exception as e:
            log.warning(f"Error processing row: {e}")  # Log any error processing a row
            continue  # Skip the problematic row

    return gherkin_scenarios  # Return the list of Gherkin scenarios

# Save Gherkin scenarios back to an Excel file
def save_gherkin_to_excel(scenarios: List[str], excel_file: str):
    """
    Save Gherkin scenarios to an Excel file.

    Args:
        scenarios: List of Gherkin scenarios.
        excel_file: Path to the output Excel file.
    """
    try:
        output_path = os.path.join(generated_dir, excel_file)  # Get the full path for saving the output file
        pd.DataFrame({"Gherkin Scenarios": scenarios}).to_excel(output_path, index=False)  # Save scenarios to Excel
        log.info(f"Gherkin scenarios saved to {output_path}")  # Log success
    except Exception as e:
        log.error(f"Error saving Gherkin scenarios to Excel: {e}")  # Log error if saving fails

# Tool to initiate the EARS-to-Gherkin conversion
@tool
def ears_to_gherkin(tool_input, cat):
    """Convert EARS requirements in an Excel file to Gherkin syntax."""
    try:
        # If tool_input is a string, treat it as the file path
        if isinstance(tool_input, str):
            excel_file = tool_input
        elif isinstance(tool_input, dict):
            excel_file = tool_input.get("excel_file")  # Get the file path from dictionary input
        else:
            return "Invalid input format. Provide an Excel file path or a dictionary with 'excel_file'."  # Invalid input

        if not excel_file:  # If no file path is provided, return an error message
            return "Please provide an Excel file containing EARS requirements."

        gherkin_scenarios = translate_ears_excel_to_gherkin(excel_file)  # Perform the translation
        if not gherkin_scenarios:  # If no scenarios were generated, return an error
            return "Conversion failed or no valid data found in the Excel file."

        save_gherkin_to_excel(gherkin_scenarios, f"gherkin_{os.path.basename(excel_file)}")  # Save the scenarios to a new Excel file
        return "EARS to Gherkin conversion completed successfully."  # Success message
    except Exception as e:
        log.error(f"Error during EARS to Gherkin conversion: {e}")  # Log error if something fails
        return f"An error occurred during the conversion: {e}"  # Return the error message

# Hook for customizing responses
@hook(priority=0)
def ears2gherkin_hook(message, cat):
    """Custom hook to rephrase responses or handle special commands."""
    user_message = message["content"]  # Extract user message from the input
    if user_message.startswith("ears2g"):  # If the message starts with 'ears2g', handle it
        # Define responses based on commands like 'train' or 'convert'
        response = {
            "train": "Training is not supported for EARS-to-Gherkin.",  # Message for unsupported command
            "convert": (
                "To convert EARS to Gherkin, type: 'ears2g convert excel-file.xlsx'. "
                "Ensure the Excel file contains SYS, Natural, and EARS columns."
            ),
        }.get(user_message.split()[1], "Unsupported EARS2Gherkin command.")  # Return appropriate response
        message["content"] = response  # Update the message with the response
    return message  # Return the modified message
