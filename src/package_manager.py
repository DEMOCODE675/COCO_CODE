"""
Package manager module.
Orchestrates package resolution and installation for the setup process.
"""

import json
from typing import List, Dict, Tuple
from src.logger import Logger
from src.validator import InputValidator
from src.error_handler import ConfigurationError


class PackageManager:
    """Manages package resolution and installation orchestration"""

    def __init__(self, logger: Logger, config_path: str = "config.json"):
        self.logger = logger
        self.config = self._load_config(config_path)
        self.selections = {
            "frameworks": [],
            "styling": [],
            "databases": [],
            "utilities": [],
        }

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )
        except json.JSONDecodeError:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {config_path}"
            )

    def add_selection(self, category: str, items: List[str]) -> bool:
        """
        Add items to a category selection
        
        Args:
            category: Category (frameworks, styling, databases, utilities)
            items: List of items to add
            
        Returns:
            True if successful
        """
        if category not in self.selections:
            self.logger.warning(f"Unknown category: {category}")
            return False

        # Validate and add items
        valid_items = []
        for item in items:
            item_lower = item.lower()

            # Check if exists in config or treat as custom
            exists = False
            for sub_category in self.config:
                if sub_category == category and item_lower in self.config[sub_category]:
                    exists = True
                    break

            if exists or item_lower not in self.selections[category]:
                valid_items.append(item_lower)

        self.selections[category].extend(valid_items)
        self.logger.debug(f"Added {len(valid_items)} items to {category}")
        return True

    def get_packages_for_selection(self) -> Tuple[List[str], List[str]]:
        """
        Get all packages and devDependencies for current selections
        
        Returns:
            Tuple of (packages, devDependencies)
        """
        all_packages = []
        all_dev_packages = []

        # Process each category
        for category, items in self.selections.items():
            if category not in self.config:
                continue

            for item in items:
                item_lower = item.lower()
                if item_lower in self.config[category]:
                    item_config = self.config[category][item_lower]
                    all_packages.extend(item_config.get("packages", []))
                    all_dev_packages.extend(item_config.get("devDependencies", []))
                else:
                    # Treat as custom/unknown package
                    all_packages.append(item_lower)

        # Remove duplicates while preserving order
        all_packages = list(dict.fromkeys(all_packages))
        all_dev_packages = list(dict.fromkeys(all_dev_packages))

        return all_packages, all_dev_packages

    def suggest_packages_for_project_type(self, project_type: str) -> Dict[str, List[str]]:
        """
        Suggest default packages based on project type
        
        Args:
            project_type: Type of project (frontend, backend, fullstack)
            
        Returns:
            Dict with suggested packages
        """
        suggestions = {
            "frameworks": [],
            "styling": [],
            "databases": [],
            "utilities": [],
        }

        project_type_lower = project_type.lower()

        if project_type_lower not in self.config.get("projectTemplates", {}):
            return suggestions

        template = self.config["projectTemplates"][project_type_lower]

        # Add default framework
        if "defaultFramework" in template:
            default_fw = template["defaultFramework"]
            if default_fw in self.config.get("frameworks", {}):
                suggestions["frameworks"].append(default_fw)

        # Add default styling
        if "defaultStyling" in template:
            default_style = template["defaultStyling"]
            if default_style in self.config.get("styling", {}):
                suggestions["styling"].append(default_style)

        # Add default database
        if "defaultDatabase" in template:
            default_db = template["defaultDatabase"]
            if default_db in self.config.get("databases", {}):
                suggestions["databases"].append(default_db)

        return suggestions

    def list_available_options(self, category: str) -> List[str]:
        """
        List all available options in a category
        
        Args:
            category: Category to list (frameworks, styling, databases, utilities)
            
        Returns:
            List of available options
        """
        if category not in self.config:
            return []

        options = []
        for key, details in self.config[category].items():
            description = details.get("description", "")
            options.append(f"  - {key}: {description}")

        return options

    def display_suggestions(self, suggestions: Dict[str, List[str]]) -> None:
        """Display suggested packages to user"""
        self.logger.info("📋 Suggested packages based on project type:")
        for category, items in suggestions.items():
            if items:
                self.logger.info(f"  {category}: {', '.join(items)}")

    def display_available_packages(self) -> None:
        """Display all available packages in each category"""
        self.logger.header("Available Packages")

        for category in self.selections.keys():
            if category in self.config:
                self.logger.info(f"\n{category.upper()}:")
                for option in self.list_available_options(category):
                    print(option)
