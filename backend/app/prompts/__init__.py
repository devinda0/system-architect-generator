"""
Prompt Templates Library

This module provides a comprehensive collection of prompt templates for:
- Role-playing system prompts
- Chain-of-thought templates
- Structured output templates
"""

from .role_playing import RolePlayingPrompts
from .chain_of_thought import ChainOfThoughtPrompts
from .structured_output import StructuredOutputPrompts

__all__ = [
    "RolePlayingPrompts",
    "ChainOfThoughtPrompts",
    "StructuredOutputPrompts",
]
