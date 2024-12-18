import os
import re
import pandas as pd
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from cat.mad_hatter.decorators import tool, hook, plugin
from cat.log import log

# Directory e impostazioni (assicurati che nl2gherkin_dir sia definito nel tuo ambiente)
nl2gherkin_dir = os.path.dirname(os.path.abspath(__file__)) # o il percorso corretto
os.environ['nl2gherkin_dir'] = nl2gherkin_dir

class LanguageSelect(Enum):
    EN = 'English'
    IT = 'Italian'

class EARSToGherkinSettings(BaseModel):
    Language: LanguageSelect = LanguageSelect.EN

@plugin
def settings_schema():
    return EARSToGherkinSettings.schema()

def ears_to_gherkin(ears_requirement: str) -> Optional[str]:
    """Converte un requisito EARS in Gherkin."""
    try:
        regex_patterns = {
            "MUST": r"The (.*) MUST (.*)",
            "SHOULD": r"The (.*) SHOULD (.*)",
            "MAY": r"The (.*) MAY (.*)",
            "WILL": r"The (.*) WILL (.*)",
            "CAN": r"The (.*) CAN (.*)",
        }

        for keyword, pattern in regex_patterns.items():
            match = re.match(pattern, ears_requirement, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                action = match.group(2).strip()

                if keyword in ["MUST", "SHOULD", "WILL"]:
                    gherkin = f"Scenario: {subject} {action}\n"
                    gherkin += f"  Given {subject} exists\n"
                    gherkin += f"  When the user performs {action}\n"
                    gherkin += f"  Then the system shall {action}\n"
                elif keyword == "MAY":
                    gherkin = f"Scenario: {subject} may {action}\n"
                    gherkin += f"  Given {subject} exists\n"
                    gherkin += f"  When the user chooses to {action}\n"
                    gherkin += f"  Then the system may {action}\n"
                elif keyword == "CAN":
                    gherkin = f"Scenario: {subject} can {action}\n"
                    gherkin += f"  Given {subject} exists\n"
                    gherkin += f"  When the user attempts to {action}\n"
                    gherkin += f"  Then the system allows the user to {action}\n"
                return gherkin
        return None
    except Exception as e:
        log.error(f"Errore durante la conversione EARS-Gherkin: {e}")
        return None

def learn_excel_to_gherkin_ears(excel_file: str) -> Optional[List[Dict]]:
    """Legge il file Excel con EARS e li prepara per l'addestramento."""
    try:
        excel_path = os.path.join(nl2gherkin_dir, excel_file)
        df = pd.read_excel(excel_path)
        gherkin_specifications = []

        for _, row in df.iterrows():
            ears_text = str(row['EARS Requirement']) # Assumi che la colonna si chiami 'EARS Requirement'
            gherkin_content = ears_to_gherkin(ears_text)

            if gherkin_content:
                example = {
                    'ears': ears_text,
                    'gherkin': gherkin_content
                }
                gherkin_specifications.append(example)
            else:
                log.warning(f"Nessuna corrispondenza EARS trovata per: {ears_text}")

        return gherkin_specifications
    except FileNotFoundError:
        log.error(f"File Excel {excel_file} non trovato in {nl2gherkin_dir}")
        return None
    except Exception as e:
        log.error(f"Errore durante la lettura del file Excel {excel_file}: {e}")
        return None

def invoke_llm_to_learn_ears(examples: List[Dict], cat):
    """Invoca l'LLM per imparare da esempi EARS-Gherkin."""
    prompt = """
    Guida alla Conversione di Requisiti EARS in Sintassi Gherkin

    ... (Prompt completo come nella risposta precedente)
    """
    try:
        i = 1
        for example in examples:
            prompt += f"""
            ESEMPIO #{i}
            INPUT: {example['ears']}
            OUTPUT:
            ```gherkin
            {example['gherkin']}
            ```
            """
            i += 1

        cat.llm(prompt)
    except Exception as e:
        log.error(f"Errore durante l'invocazione dell'LLM per EARS: {e}")

def train_ears_to_gherkin(excel_file_name: str, cat) -> str:
    """Addestra il sistema con esempi da un file Excel (EARS)."""
    try:
        training_data = learn_excel_to_gherkin_ears(excel_file_name)
        if training_data is None:
            return "Failed to read training data from Excel file."

        examples = []
        for data in training_data:
            examples.append({
                "ears": data['ears'],
                "gherkin": data['gherkin']
            })
        invoke_llm_to_learn_ears(examples, cat)

        return "Training EARS to Gherkin completed successfully"
    except Exception as e:
        log.error(f"Errore durante l'addestramento EARS-Gherkin: {e}")
        return "An error occurred during the training"

def do_convert_ears_to_gherkin(ears_text: str, cat) -> Optional[str]:
    """Esegue la conversione da EARS a Gherkin usando l'LLM addestrato."""
    prompt = f"""
    Converti il seguente requisito EARS in Gherkin:

    INPUT: {ears_text}

    OUTPUT:
    """

    try:
        llm_response = cat.llm(prompt)
        return llm_response
    except Exception as e:
        log.error(f"Errore durante la conversione EARS-Gherkin con LLM: {e}")
        return None

@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Dict:
    """Gestisce le risposte rapide dell'agente (con comandi EARS)."""
    return_direct = False
    user_message = cat.working_memory["user_message_json"]["text"]
    excel_filename = "ears_example.xlsx"

    if user_message.startswith("ears"):
        _, *args = user_message.split(maxsplit=1)
        if args:
            if args[0].startswith("convert"):
                _, *subargs = args[0].split(maxsplit=1)
                if subargs:
                    ears_text = " ".join(subargs) # Gestisce input con spazi
                    response = do_convert_ears_to_gherkin(ears_text, cat)
                    if response:
                        return {"output": response}
                    else:
                        return {"output": "Conversione fallita."}
                else:
                     return {"output": "Please, provide a EARS requirement to convert: ears convert \"The system MUST do something\""}

            if args[0].startswith("train"):
                response = train_ears_to_gherkin(excel_filename, cat)
                return {"output": response}
        else:
            response = ("How to train the cat to convert EARS to gherkin:"
                        "\nType: ears train"
                        "\nHow to convert an EARS sentence:"
                        "\nType: ears convert \"The system MUST do something\"")
            return_direct = True

    if return_direct:
        return {"output": response}

    return fast_reply
