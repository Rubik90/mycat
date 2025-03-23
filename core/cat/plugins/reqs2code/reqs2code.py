import os
import re
import pandas as pd
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from cat.log import log
from cat.mad_hatter.decorators import hook, plugin
from cat.looking_glass.cheshire_cat import CheshireCat

# Set plugin directory
reqs2code_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['reqs2code_dir'] = reqs2code_dir

# Settings for code generation
class CodeLanguage(Enum):
    EMBEDDED_C = 'Embedded C'

class Reqs2CodeSettings(BaseModel):
    Language: CodeLanguage = CodeLanguage.EMBEDDED_C

@plugin
def settings_schema():
    return Reqs2CodeSettings.model_json_schema()

def load_requirements_from_excel() -> Optional[pd.DataFrame]:
    """Load requirements from the Excel file."""
    try:
        excel_path = os.path.join(reqs2code_dir, 'req.xlsx')
        df = pd.read_excel(excel_path)
        
        if 'ID' not in df.columns or 'REQUIREMENT' not in df.columns:
            log.error("Excel file must contain 'ID' and 'REQUIREMENT' columns")
            return None
            
        return df
    except FileNotFoundError:
        log.error(f"Excel file 'req.xlsx' not found in {reqs2code_dir}")
    except Exception as e:
        log.error(f"Error reading Excel file: {e}")
    return None

def generate_embedded_c_code(requirement: str) -> str:
    """Convert a requirement into embedded C code."""
    # Basic template for embedded C code
    code = """
#include <stdint.h>
#include "stm32f4xx_hal.h"

// Function prototype
void process_requirement(void);

// Timer configuration
static TIM_HandleTypeDef htim;

// GPIO configuration
static GPIO_InitTypeDef GPIO_InitStruct;

// Initialize hardware
void init_hardware(void) {
    // Enable peripheral clocks
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();
    
    // Configure GPIO
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // Configure timer
    htim.Instance = TIM2;
    htim.Init.Period = 1000 - 1;
    htim.Init.Prescaler = 84 - 1;
    htim.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim.Init.CounterMode = TIM_COUNTERMODE_UP;
    HAL_TIM_Base_Init(&htim);
}

// Main process function
void process_requirement(void) {
    // TODO: Implement specific requirement logic here
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
    HAL_Delay(1000);
}

// Main function
int main(void) {
    HAL_Init();
    init_hardware();
    
    while (1) {
        process_requirement();
    }
}
"""
    return code

def save_generated_code(code: str, req_id: str) -> bool:
    """Save the generated code to a file."""
    try:
        generated_dir = os.path.join(reqs2code_dir, 'generated')
        os.makedirs(generated_dir, exist_ok=True)
        
        file_path = os.path.join(generated_dir, f'req_{req_id}.c')
        with open(file_path, 'w') as f:
            f.write(code)
            
        return True
    except Exception as e:
        log.error(f"Error saving generated code: {e}")
        return False

@hook
def agent_prompt_prefix(prefix: str, cat: CheshireCat) -> str:
    """Add plugin-specific instructions to the agent's prompt."""
    return prefix + """
You can use the following commands to interact with the Reqs2Code plugin:
- `reqs2code convert`: Convert requirements to embedded C code
- `reqs2code help`: Show help information
"""

@hook
def agent_prompt_function(user_message: str, cat: CheshireCat) -> str:
    """Process user commands for the plugin."""
    if user_message.strip().lower() == 'reqs2code help':
        return """Reqs2Code Plugin Commands:
- reqs2code convert: Convert requirements from req.xlsx to embedded C code
- reqs2code help: Show this help message"""
    
    if user_message.strip().lower() == 'reqs2code convert':
        df = load_requirements_from_excel()
        if df is None:
            return "Failed to load requirements from Excel file."
            
        success_count = 0
        for _, row in df.iterrows():
            req_id = str(row['ID'])
            requirement = str(row['REQUIREMENT'])
            
            code = generate_embedded_c_code(requirement)
            if save_generated_code(code, req_id):
                success_count += 1
                
        return f"Successfully generated {success_count} C files from requirements."
        
    return user_message

