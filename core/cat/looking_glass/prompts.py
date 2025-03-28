
TOOL_PROMPT = """Create a JSON with the correct "action" and "action_input" to help the Human.
You can use one of these actions:
{tools}
- "no_action": Use this action if no relevant action is available. Input is always null.

## The JSON must have the following structure:

```json
{{
    "action": // str - The name of the action to take, should be one of [{tool_names}, "no_action"]
    "action_input": // str or null - The input to the action according to its description
}}
```

{examples}
"""


MAIN_PROMPT_PREFIX = """You are my AI Assistant."""


MAIN_PROMPT_SUFFIX = """

# Context
{episodic_memory}

{declarative_memory}

{tools_output}
"""
