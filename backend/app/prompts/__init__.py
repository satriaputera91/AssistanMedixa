"""
Centralized Prompts Package for AssistantMedixa Backend.
Contains prompt templates, system instructions, and GenAI function calling declarations
for all medical agent skills.
"""

from app.prompts.planner_prompts import (
    PLANNER_SYSTEM_INSTRUCTION,
    CLASSIFY_INTENT_FUNCTION_DECLARATION,
    PATIENT_INTENTS_LIST,
    GENERAL_INTENTS_LIST,
    build_planner_prompt
)
from app.prompts.anamnesis_prompts import (
    PATIENT_HISTORY_INSTRUCTION,
    PATIENT_ANAMNESIS_INSTRUCTION
)
from app.prompts.synthesis_prompts import (
    SYNTHESIS_BASE_INSTRUCTION,
    GREETING_INSTRUCTION,
    NO_PATIENT_SELECTED_GUIDE
)

__all__ = [
    "PLANNER_SYSTEM_INSTRUCTION",
    "CLASSIFY_INTENT_FUNCTION_DECLARATION",
    "PATIENT_INTENTS_LIST",
    "GENERAL_INTENTS_LIST",
    "build_planner_prompt",
    "PATIENT_HISTORY_INSTRUCTION",
    "PATIENT_ANAMNESIS_INSTRUCTION",
    "SYNTHESIS_BASE_INSTRUCTION",
    "GREETING_INSTRUCTION",
    "NO_PATIENT_SELECTED_GUIDE",
]
