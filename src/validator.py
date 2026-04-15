"""
Validator module for user input validation.
Ensures project names, types, and other inputs meet requirements.
"""

import re
from typing import Tuple


class InputValidator:
    """Validates user inputs for project setup"""

    @staticmethod
    def validate_project_name(name: str) -> Tuple[bool, str]:
        """
        Validate project name:
        - Only alphanumeric, hyphens, underscores
        - 2-50 characters
        - Cannot start with number
        """
        if not name or len(name) < 2 or len(name) > 50:
            return False, "Project name must be 2-50 characters long"

        if not re.match(r"^[a-zA-Z_][-a-zA-Z0-9_]*$", name):
            return (
                False,
                "Project name can only contain letters, numbers, hyphens, and underscores",
            )

        return True, "Valid"

    @staticmethod
    def validate_choice(choice: str, valid_options: list) -> Tuple[bool, str]:
        """Validate choice against available options"""
        if choice.lower() not in valid_options:
            return (
                False,
                f"Invalid choice. Valid options: {', '.join(valid_options)}",
            )
        return True, "Valid"

    @staticmethod
    def validate_language(language: str) -> Tuple[bool, str]:
        """Validate programming language choice"""
        valid_languages = ["javascript", "typescript", "python"]
        return InputValidator.validate_choice(language.lower(), valid_languages)

    @staticmethod
    def validate_project_type(project_type: str) -> Tuple[bool, str]:
        """Validate project type choice"""
        valid_types = ["frontend", "backend", "fullstack", "mobile"]
        return InputValidator.validate_choice(project_type.lower(), valid_types)

    @staticmethod
    def sanitize_library_input(user_input: str) -> list:
        """
        Convert user input into list of libraries.
        Handles: "react tailwind axios" -> ["react", "tailwind", "axios"]
        """
        # Split by spaces, commas, or both
        libraries = re.split(r"[\s,]+", user_input.strip())
        # Filter empty strings and convert to lowercase
        return [lib.lower() for lib in libraries if lib.strip()]

    @staticmethod
    def validate_not_empty(value: str, field_name: str = "Input") -> Tuple[bool, str]:
        """Ensure input is not empty"""
        if not value or not value.strip():
            return False, f"{field_name} cannot be empty"
        return True, "Valid"
