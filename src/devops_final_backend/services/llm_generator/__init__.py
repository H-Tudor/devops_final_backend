"""LLM Generator

This package allows for definition of specialized single-task LLM generators starting from an abstract generator.
It exposes
- the specialized generators (currently just the Composer Generator)
- the llm response model
- the errors that can occur during the generation process
"""

from .compose_generator import ComposeGenerator

__all__ = [
    "ComposeGenerator",
    "models",
    "errors",
]
