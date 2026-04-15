"""
Configuration file generator module.
Creates tsconfig.json, tailwind.config.js, and other configuration files.
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from src.logger import Logger
from src.error_handler import FileOperationError


class ConfigGenerator:
    """Generates configuration files for projects"""

    def __init__(self, logger: Logger):
        self.logger = logger

    def generate_tsconfig(
        self, project_path: str, language: str, frameworks: List[str]
    ) -> bool:
        """
        Generate tsconfig.json for TypeScript projects
        
        Args:
            project_path: Root project path
            language: Programming language
            frameworks: List of selected frameworks
            
        Returns:
            True if successful or not needed
        """
        if language.lower() != "typescript":
            return True

        tsconfig_path = os.path.join(project_path, "tsconfig.json")

        if "next" in [fw.lower() for fw in frameworks]:
            next_config = {
                "compilerOptions": {
                    "target": "ES2020",
                    "lib": ["DOM", "DOM.Iterable", "ESNext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "ESNext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                },
                "include": ["next-env.d.ts", "src/**/*.ts", "src/**/*.tsx", "src/**/*.d.ts"],
                "exclude": ["node_modules"],
            }

            try:
                with open(tsconfig_path, "w") as f:
                    json.dump(next_config, f, indent=2)
                self.logger.step("Generated tsconfig.json")
                return True
            except Exception as e:
                raise FileOperationError(f"Failed to generate tsconfig.json: {e}")

        config = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "noImplicitAny": True,
                "strictNullChecks": True,
                "strictFunctionTypes": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noImplicitReturns": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
            },
            "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.d.ts"],
            "exclude": ["node_modules", "dist"],
        }

        # Add React/JSX specific options
        if any(fw in frameworks for fw in ["react", "next"]):
            config["compilerOptions"]["jsx"] = "react-jsx"

        try:
            with open(tsconfig_path, "w") as f:
                json.dump(config, f, indent=2)
            self.logger.step("Generated tsconfig.json")
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to generate tsconfig.json: {e}")

    def generate_tailwind_config(
        self, project_path: str, styling_options: List[str]
    ) -> bool:
        """
        Generate tailwind.config.js and postcss.config.js

        Args:
            project_path: Root project path
            styling_options: List of selected styling options

        Returns:
            True if successful or not needed
        """
        if "tailwind" not in styling_options:
            return True

        config_path = os.path.join(project_path, "tailwind.config.js")
        postcss_path = os.path.join(project_path, "postcss.config.js")

        tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#3b82f6",
        secondary: "#ef4444",
      },
    },
  },
  plugins: [],
}
'''

        postcss_config = '''export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
'''

        try:
            with open(config_path, "w") as f:
                f.write(tailwind_config)

            with open(postcss_path, "w") as f:
                f.write(postcss_config)

            self.logger.step("Generated tailwind.config.js and postcss.config.js")
            return True

        except Exception as e:
            raise FileOperationError(f"Failed to generate Tailwind config: {e}")

    def generate_default_postcss_config(self, project_path: str) -> bool:
        """Generate a default local PostCSS config to avoid inheriting global configs."""
        postcss_path = os.path.join(project_path, "postcss.config.js")
        postcss_config = '''export default {
  plugins: {},
}
'''

        try:
            with open(postcss_path, "w") as f:
                f.write(postcss_config)

            self.logger.step("Generated default postcss.config.js")
            return True

        except Exception as e:
            raise FileOperationError(f"Failed to generate default postcss config: {e}")

    def generate_package_json_scripts(
        self,
        project_path: str,
        language: str,
        frameworks: List[str],
        package_json: Dict,
    ) -> Dict:
        """
        Generate appropriate scripts for package.json
        
        Args:
            project_path: Root project path
            language: Programming language
            frameworks: List of selected frameworks
            package_json: Existing package.json dict
            
        Returns:
            Updated package.json dict
        """
        scripts = {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
        }

        framework_set = {fw.lower() for fw in frameworks}

        # Add TypeScript build if needed
        if language.lower() == "typescript":
            scripts["typecheck"] = "tsc --noEmit"

        # Add framework-specific scripts
        if "react-native" in framework_set:
            scripts = {
                "dev": "expo start --go",
                "dev:auto": "expo start --go --tunnel || expo start --go",
                "dev:tunnel": "expo start --go --tunnel",
                "dev:clear": "expo start --go --clear",
                "start": "expo start --go",
                "android": "expo run:android",
                "ios": "expo run:ios",
                "web": "expo start --web",
            }
        elif "next" in framework_set:
            scripts["dev"] = "next dev"
            scripts["build"] = "next build"
            scripts["start"] = "next start"

        elif "express" in framework_set:
            if language.lower() == "typescript":
                scripts["dev"] = "ts-node src/server.ts"
                scripts["build"] = "tsc"
                scripts["start"] = "node dist/server.js"
            else:
                scripts["dev"] = "node src/server.js"
                scripts["build"] = "echo No build step for JavaScript backend"
                scripts["start"] = "node src/server.js"

        elif "fastapi" in framework_set:
            scripts = {
                "dev": "python -m uvicorn src.main:app --reload",
                "start": "python -m uvicorn src.main:app",
            }

        elif "django" in framework_set:
            scripts = {
                "dev": "python src/manage.py runserver",
                "start": "python src/manage.py runserver",
            }

        # Add testing script if Jest is included
        if "jest" in framework_set:
            scripts["test"] = "jest"
            scripts["test:watch"] = "jest --watch"

        # Add linting
        if "eslint" in framework_set:
            scripts["lint"] = "eslint src --max-warnings=0"
            scripts["lint:fix"] = "eslint src --fix"

        package_json["scripts"] = scripts
        return package_json

    def update_package_json(
        self,
        project_path: str,
        project_name: str,
        language: str,
        frameworks: List[str],
    ) -> bool:
        """
        Update package.json with project metadata and scripts
        
        Args:
            project_path: Root project path
            project_name: Project name
            language: Programming language
            frameworks: List of selected frameworks
            
        Returns:
            True if successful
        """
        package_json_path = os.path.join(project_path, "package.json")

        try:
            # Read existing package.json
            with open(package_json_path, "r") as f:
                package_json = json.load(f)

            # Update metadata
            package_json["name"] = project_name
            package_json["description"] = f"A {language} project created with COCO_CODE CLI"
            package_json["version"] = "1.0.0"

            framework_set = {fw.lower() for fw in frameworks}
            if any(fw in framework_set for fw in ["next", "react-native", "fastapi", "django"]):
                package_json.pop("type", None)
            else:
                package_json["type"] = "module"

            if "react-native" in framework_set:
                package_json["main"] = "node_modules/expo/AppEntry.js"

            # Generate and add scripts
            package_json = self.generate_package_json_scripts(
                project_path, language, frameworks, package_json
            )

            # Write back
            with open(package_json_path, "w") as f:
                json.dump(package_json, f, indent=2)

            self.logger.step("Updated package.json with scripts and metadata")
            return True

        except Exception as e:
            raise FileOperationError(f"Failed to update package.json: {e}")

    def generate_vite_config(self, project_path: str, frameworks: List[str]) -> bool:
        """
        Generate vite.config.js
        
        Args:
            project_path: Root project path
            frameworks: List of selected frameworks
            
        Returns:
            True if successful
        """
        vite_config_path = os.path.join(project_path, "vite.config.js")

        plugins = []
        if "react" in frameworks:
            plugins.append("react()")

        if "vue" in frameworks:
            plugins.append("vue()")

        if "svelte" in frameworks:
            plugins.append("svelte()")

        plugins_str = ",\n    ".join(plugins)
        plugins_block = f"[\n    {plugins_str}\n  ]" if plugins_str else "[]"

        vite_config = f'''import {{ defineConfig }} from 'vite'
{"import react from '@vitejs/plugin-react'" if "react" in frameworks else ""}
{"import vue from '@vitejs/plugin-vue'" if "vue" in frameworks else ""}
{"import { svelte } from '@sveltejs/vite-plugin-svelte'" if "svelte" in frameworks else ""}

export default defineConfig({{
    plugins: {plugins_block},
  server: {{
    port: 3000,
    open: true,
  }},
}})
'''

        try:
            with open(vite_config_path, "w") as f:
                f.write(vite_config)

            self.logger.step("Generated vite.config.js")
            return True

        except Exception as e:
            raise FileOperationError(f"Failed to generate vite.config.js: {e}")

