"""
Interactive CLI interface for the COCO_CODE CLI.
Main entry point for user interaction.
"""

import os
import sys
import re
from pathlib import Path
from src.logger import Logger
from src.validator import InputValidator
from src.package_manager import PackageManager
from src.project_generator import ProjectGenerator
from src.config_generator import ConfigGenerator
from src.package_installer import PackageInstaller
from src.error_handler import ErrorHandler, ProjectSetupException


class ProjectSetupCLI:
    """Interactive CLI for project setup"""

    def __init__(self):
        self.logger = Logger(verbose=False)
        self.validator = InputValidator()
        self.package_manager = None
        self.project_generator = None
        self.config_generator = None
        self.package_installer = None

    def welcome(self) -> None:
        """Display welcome message"""
        self.logger.header("[*] COCO_CODE CLI")
        print("""
Welcome to the ultimate COCO_CODE CLI!

This tool will help you create a new project with:
[*] Dynamic package selection
[*] Automatic configuration
[*] Smart dependency management
[*] Ready-to-start project structure

Let's get started!
""")

    def collect_basic_info(self) -> dict:
        """
        Collect basic project information from user
        
        Returns:
            Dict with project name, type, and language
        """
        info = {}

        # Project Name
        while True:
            project_name = input("\n[?] Project name: ").strip()
            valid, message = self.validator.validate_project_name(project_name)
            if valid:
                info["name"] = project_name
                break
            self.logger.error(message)

        # Project Type
        project_types = ["frontend", "backend", "fullstack", "mobile"]
        self.logger.info("Select project type:")
        for i, ptype in enumerate(project_types, 1):
            print(f"  {i}. {ptype}")

        while True:
            project_type_input = input("\nSelect (1-4): ").strip()
            try:
                idx = int(project_type_input) - 1
                if 0 <= idx < len(project_types):
                    info["type"] = project_types[idx]
                    break
            except ValueError:
                pass
            self.logger.error("Invalid selection. Enter a number 1-4")

        # Language
        languages = ["javascript", "typescript"]
        self.logger.info("Select language:")
        for i, lang in enumerate(languages, 1):
            print(f"  {i}. {lang}")

        while True:
            lang_input = input("\nSelect (1-2): ").strip()
            try:
                idx = int(lang_input) - 1
                if 0 <= idx < len(languages):
                    info["language"] = languages[idx]
                    break
            except ValueError:
                pass
            self.logger.error("Invalid selection. Enter a number 1-2")

        self.logger.success(
            f"Project: {info['name']} ({info['type']}, {info['language']})"
        )
        return info

    def _resolve_menu_selections(
        self,
        user_input: str,
        available_options: list,
        category_name: str,
    ) -> list:
        """
        Resolve menu input into valid option names.
        Supports numeric indexes ("1 2"), ranges ("1-3"), "all" and names.
        """
        tokens = self.validator.sanitize_library_input(user_input)
        if not tokens:
            return []

        option_lookup = {option.lower(): option for option in available_options}
        resolved = []
        invalid = []
        max_index = len(available_options)

        for token in tokens:
            if token in ["all", "*"]:
                resolved.extend(available_options)
                continue

            range_match = re.match(r"^(\d+)-(\d+)$", token)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))

                if 1 <= start <= max_index and 1 <= end <= max_index:
                    step = 1 if start <= end else -1
                    for idx in range(start, end + step, step):
                        resolved.append(available_options[idx - 1])
                else:
                    invalid.append(token)
                continue

            if token.isdigit():
                index = int(token) - 1
                if 0 <= index < len(available_options):
                    resolved.append(available_options[index])
                else:
                    invalid.append(token)
                continue

            if token in option_lookup:
                resolved.append(option_lookup[token])
            else:
                invalid.append(token)

        resolved = list(dict.fromkeys(resolved))

        if invalid:
            self.logger.warning(
                f"Ignored invalid {category_name} selections: {', '.join(invalid)}"
            )

        return resolved

    def collect_dependencies(self) -> dict:
        """
        Collect framework and library preferences
        
        Returns:
            Dict with selected dependencies
        """
        selections = {
            "frameworks": [],
            "styling": [],
            "databases": [],
            "utilities": [],
        }

        # Get suggestions
        suggestions = self.package_manager.suggest_packages_for_project_type(
            self.project_info["type"]
        )

        self.logger.info("\n[*] Suggested packages based on your project type:")
        for category, items in suggestions.items():
            if items:
                self.logger.info(f"  {category}: {', '.join(items)}")

        # Framework selection
        self.logger.info("\n[*] Available Frameworks:")
        frameworks = list(self.package_manager.config.get("frameworks", {}).keys())
        for i, fw in enumerate(frameworks, 1):
            details = self.package_manager.config["frameworks"][fw]
            print(f"  {i}. {fw} - {details.get('description', '')}")

        print(
            "  (Type numbers, names, ranges like 1-3, or all; press Enter to skip)"
        )
        fw_input = input("Select frameworks: ").strip()
        if fw_input:
            fw_list = self._resolve_menu_selections(
                fw_input, frameworks, "framework"
            )
            if fw_list:
                selections["frameworks"] = fw_list
                self.logger.success(f"Selected frameworks: {', '.join(fw_list)}")
            else:
                self.logger.warning("No valid frameworks selected")

        # Styling selection
        self.logger.info("\n[*] Available Styling Options:")
        styling = list(self.package_manager.config.get("styling", {}).keys())
        for i, style in enumerate(styling, 1):
            details = self.package_manager.config["styling"][style]
            print(f"  {i}. {style} - {details.get('description', '')}")

        print(
            "  (Type numbers, names, ranges like 1-3, or all; press Enter to skip)"
        )
        style_input = input("Select styling: ").strip()
        if style_input:
            style_list = self._resolve_menu_selections(
                style_input, styling, "styling"
            )
            if style_list:
                selections["styling"] = style_list
                self.logger.success(f"Selected styling: {', '.join(style_list)}")
            else:
                self.logger.warning("No valid styling options selected")

        # Database selection
        self.logger.info("\n[*] Available Databases:")
        databases = list(self.package_manager.config.get("databases", {}).keys())
        for i, db in enumerate(databases, 1):
            details = self.package_manager.config["databases"][db]
            print(f"  {i}. {db} - {details.get('description', '')}")

        print(
            "  (Type numbers, names, ranges like 1-3, or all; press Enter to skip)"
        )
        db_input = input("Select databases: ").strip()
        if db_input:
            db_list = self._resolve_menu_selections(
                db_input, databases, "database"
            )
            if db_list:
                selections["databases"] = db_list
                self.logger.success(f"Selected databases: {', '.join(db_list)}")
            else:
                self.logger.warning("No valid databases selected")

        # Utilities selection
        self.logger.info("\n[*] Available Utilities:")
        utilities = list(self.package_manager.config.get("utilities", {}).keys())
        for i, util in enumerate(utilities, 1):
            details = self.package_manager.config["utilities"][util]
            print(f"  {i}. {util} - {details.get('description', '')}")

        print(
            "  (Type numbers, names, ranges like 1-3, or all; press Enter to skip)"
        )
        util_input = input("Select utilities: ").strip()
        if util_input:
            util_list = self._resolve_menu_selections(
                util_input, utilities, "utility"
            )
            if util_list:
                selections["utilities"] = util_list
                self.logger.success(f"Selected utilities: {', '.join(util_list)}")
            else:
                self.logger.warning("No valid utilities selected")

        # Mobile projects always need React Native + native styling baseline.
        if self.project_info.get("type", "").lower() == "mobile":
            selected_frameworks = {fw.lower() for fw in selections["frameworks"]}
            if "react-native" not in selected_frameworks:
                default_mobile_frameworks = suggestions.get("frameworks") or ["react-native"]
                selections["frameworks"] = list(
                    dict.fromkeys(selections["frameworks"] + default_mobile_frameworks)
                )
                self.logger.info(
                    f"Applied mobile default framework: {', '.join(default_mobile_frameworks)}"
                )

            if not selections["styling"]:
                default_mobile_styling = suggestions.get("styling") or ["native"]
                selections["styling"] = list(dict.fromkeys(default_mobile_styling))
                self.logger.info(
                    f"Applied mobile default styling: {', '.join(default_mobile_styling)}"
                )

        # Custom packages
        print("\n[*] Custom packages (advanced):")
        print(
            "  Enter any npm packages not listed above (space or comma separated)"
        )
        custom_input = input("Custom packages (or press Enter to skip): ").strip()
        if custom_input:
            custom_list = self.validator.sanitize_library_input(custom_input)
            selections["utilities"].extend(custom_list)
            self.logger.success(f"Added custom packages: {', '.join(custom_list)}")

        return selections

    def confirm_setup(self, selections: dict, packages: tuple) -> bool:
        """
        Show summary and confirm setup
        
        Args:
            selections: User selections
            packages: Tuple of (packages, devDependencies)
            
        Returns:
            True if user confirms
        """
        self.logger.header("Setup Summary")

        print(f"Project Name: {self.project_info['name']}")
        print(f"Type: {self.project_info['type']}")
        print(f"Language: {self.project_info['language']}")
        print("\nSelected Packages:")
        for category, items in selections.items():
            if items:
                print(f"  {category}: {', '.join(items)}")

        prod_pkgs, dev_pkgs = packages
        print(f"\nWill install:")
        print(f"  Production: {len(prod_pkgs)} packages")
        print(f"  Development: {len(dev_pkgs)} packages")

        confirm = input("\nContinue with setup? (yes/no): ").strip().lower()
        return confirm in ["yes", "y"]

    def _augment_packages_for_project(
        self,
        packages: tuple,
        selections: dict,
    ) -> tuple:
        """Add required runtime/tooling packages based on project context."""
        prod_pkgs, dev_pkgs = packages
        prod_pkgs = list(prod_pkgs)
        dev_pkgs = list(dev_pkgs)

        frameworks = selections.get("frameworks", [])

        # Vite is required for frontend frameworks using vite scripts.
        if any(fw in ["react", "vue", "svelte"] for fw in frameworks):
            if "vite" not in dev_pkgs and "next" not in frameworks:
                dev_pkgs.append("vite")

        # TypeScript language projects need the TypeScript compiler.
        if self.project_info.get("language", "").lower() == "typescript":
            if "typescript" not in dev_pkgs:
                dev_pkgs.append("typescript")

        return (
            list(dict.fromkeys(prod_pkgs)),
            list(dict.fromkeys(dev_pkgs)),
        )

    def execute_setup(self, selections: dict, packages: tuple) -> bool:
        """
        Execute the full setup process
        
        Args:
            selections: User selections
            packages: Tuple of (packages, devDependencies)
            
        Returns:
            True if successful
        """
        try:
            project_path = os.path.join(os.getcwd(), self.project_info["name"])
            if self.project_info.get("type", "").lower() == "mobile":
                selections.setdefault("frameworks", [])
                selections.setdefault("styling", [])

                if "react-native" not in {
                    fw.lower() for fw in selections.get("frameworks", [])
                }:
                    selections["frameworks"] = list(
                        dict.fromkeys(selections["frameworks"] + ["react-native"])
                    )

                if not selections["styling"]:
                    selections["styling"] = ["native"]

            framework_set = {
                fw.lower() for fw in selections.get("frameworks", [])
            }
            prod_pkgs, dev_pkgs = packages

            npm_frameworks = {
                "react",
                "next",
                "vue",
                "svelte",
                "express",
                "react-native",
            }
            requires_npm = bool(prod_pkgs or dev_pkgs) or bool(
                framework_set.intersection(npm_frameworks)
            )

            # Create project folder
            self.logger.header("Creating Project Structure")
            self.project_generator.create_project_folder(project_path)
            self.project_generator.create_folder_structure(
                project_path, self.project_info["type"], self.project_info["language"]
            )

            if requires_npm:
                # Initialize npm
                self.logger.header("Initializing npm")
                if not self.package_installer.check_npm_installed():
                    self.logger.error("npm is not installed. Please install Node.js first.")
                    return False

                self.package_installer.init_npm_project(project_path)

                # Install packages
                self.logger.header("Installing Packages")
                self.package_installer.install_all_packages(
                    project_path,
                    {"packages": prod_pkgs},
                    {"devDependencies": dev_pkgs},
                )

                # Generate configs
                self.logger.header("Generating Configuration Files")
                self.config_generator.update_package_json(
                    project_path,
                    self.project_info["name"],
                    self.project_info["language"],
                    selections.get("frameworks", []),
                )

                if self.project_info["language"].lower() == "typescript":
                    self.config_generator.generate_tsconfig(
                        project_path,
                        self.project_info["language"],
                        selections.get("frameworks", []),
                    )

                if "tailwind" in selections.get("styling", []):
                    self.config_generator.generate_tailwind_config(
                        project_path, selections.get("styling", [])
                    )
                elif any(
                    fw in ["react", "vue", "svelte"]
                    for fw in selections.get("frameworks", [])
                ):
                    self.config_generator.generate_default_postcss_config(
                        project_path
                    )

                if any(
                    fw in ["react", "vue", "svelte"]
                    for fw in selections.get("frameworks", [])
                ):
                    self.config_generator.generate_vite_config(
                        project_path, selections.get("frameworks", [])
                    )
            else:
                self.logger.warning(
                    "No npm-based framework/packages selected. Skipping npm initialization and package installation."
                )

            # Create starter files
            self.logger.header("Creating Starter Files")
            self.project_generator.create_starter_files(
                project_path,
                self.project_info["name"],
                self.project_info["language"],
                self.project_info["type"],
                selections.get("frameworks", []),
                selections.get("styling", []),
            )

            return True

        except ProjectSetupException as e:
            ErrorHandler.handle_exception(e, self.logger, "Setup failed")
            return False

    def run(self) -> None:
        """Main entry point - run the full CLI"""
        try:
            self.welcome()

            # Initialize managers
            self.package_manager = PackageManager(self.logger)
            self.project_generator = ProjectGenerator(self.logger)
            self.config_generator = ConfigGenerator(self.logger)
            self.package_installer = PackageInstaller(self.logger)

            # Collect user input
            self.project_info = self.collect_basic_info()
            selections = self.collect_dependencies()

            # Get packages to install
            for category, items in selections.items():
                if items:
                    self.package_manager.add_selection(category, items)

            packages = self.package_manager.get_packages_for_selection()
            packages = self._augment_packages_for_project(packages, selections)

            # Show summary and confirm
            if not self.confirm_setup(selections, packages):
                self.logger.warning("Setup cancelled by user")
                return

            # Execute setup
            if self.execute_setup(selections, packages):
                self.logger.header("[*] Project Created Successfully!")
                print(f"""
Your project '{self.project_info['name']}' is ready!

Next steps:
  1. cd {self.project_info['name']}
  2. npm run dev

Happy coding!
""")
                self.logger.elapsed_time()
            else:
                self.logger.error("Setup completed with errors")

        except KeyboardInterrupt:
            self.logger.warning("\nSetup cancelled by user")
        except Exception as e:
            ErrorHandler.handle_exception(e, self.logger, "Unexpected error")


def main():
    """Entry point"""
    cli = ProjectSetupCLI()
    cli.run()


if __name__ == "__main__":
    main()

