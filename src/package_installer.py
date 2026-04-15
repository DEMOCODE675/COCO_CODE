"""
Package installer module.
Handles npm package installation and initialization.
"""

import subprocess
import os
import json
from typing import List, Dict, Tuple
from src.logger import Logger
from src.error_handler import PackageInstallationError


class PackageInstaller:
    """Manages npm packages and installation"""

    def __init__(self, logger: Logger):
        self.logger = logger

    @staticmethod
    def _summarize_npm_stderr(stderr: str) -> str:
        """Return a concise npm error summary from stderr output."""
        lines = [line.strip() for line in stderr.splitlines() if line.strip()]
        if not lines:
            return "Unknown npm error"

        priority_prefixes = [
            "npm error code",
            "npm error path",
            "npm error command",
            "npm error",
        ]

        for prefix in priority_prefixes:
            for line in lines:
                if line.lower().startswith(prefix):
                    return line

        return lines[0]

    @staticmethod
    def _get_npm_init_commands() -> List[List[str]]:
        """Return npm init command candidates by platform."""
        if os.name == "nt":
            return [
                ["npm.cmd", "init", "-y"],
                ["npm", "init", "-y"],
            ]

        return [["npm", "init", "-y"]]

    def _create_minimal_package_json(self, project_path: str) -> None:
        """Create a minimal package.json when npm init consistently times out."""
        package_json_path = os.path.join(project_path, "package.json")
        package_name = os.path.basename(os.path.abspath(project_path)) or "project"

        package_json = {
            "name": package_name,
            "version": "1.0.0",
            "description": "",
            "main": "index.js",
            "scripts": {
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "keywords": [],
            "author": "",
            "license": "ISC",
        }

        with open(package_json_path, "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)

    def check_npm_installed(self) -> bool:
        """
        Check if npm is installed and available
        
        Returns:
            True if npm is available
        """
        try:
            # Try different npm command variations for cross-platform support
            npm_commands = [
                ["npm", "--version"],
                ["npm.cmd", "--version"],
                ["npm.ps1", "--version"],
            ]
            
            for cmd in npm_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=(cmd[0].endswith('.ps1')),  # Use shell for PowerShell
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        self.logger.debug(f"npm version: {version}")
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            return False
        except Exception:
            return False

    def init_npm_project(self, project_path: str) -> bool:
        """
        Initialize npm project with npm init -y
        
        Args:
            project_path: Root project path
            
        Returns:
            True if successful
        """
        try:
            self.logger.step("Initializing npm project...")

            init_commands = self._get_npm_init_commands()
            timeout_schedule = [30, 90]
            last_error = None
            saw_timeout = False
            saw_non_timeout_failure = False

            for timeout_seconds in timeout_schedule:
                for cmd in init_commands:
                    try:
                        result = subprocess.run(
                            cmd,
                            cwd=project_path,
                            capture_output=True,
                            text=True,
                            timeout=timeout_seconds,
                        )

                        if result.returncode == 0:
                            self.logger.success("npm project initialized")
                            return True

                        error_summary = self._summarize_npm_stderr(result.stderr)
                        last_error = f"{' '.join(cmd)} failed: {error_summary}"
                        saw_non_timeout_failure = True
                        self.logger.warning(last_error)

                    except FileNotFoundError:
                        last_error = f"Command not found: {cmd[0]}"
                        saw_non_timeout_failure = True
                    except subprocess.TimeoutExpired:
                        saw_timeout = True
                        last_error = (
                            f"{' '.join(cmd)} timed out after {timeout_seconds}s"
                        )
                        self.logger.warning(last_error)

                if timeout_seconds != timeout_schedule[-1] and saw_timeout:
                    self.logger.warning(
                        "npm init is taking longer than expected; retrying with a higher timeout..."
                    )

            # If npm init only timed out (no explicit command failures), continue with fallback.
            if saw_timeout and not saw_non_timeout_failure:
                self.logger.warning(
                    "npm init timed out repeatedly. Creating a minimal package.json fallback..."
                )
                self._create_minimal_package_json(project_path)
                self.logger.success("Created fallback package.json")
                return True

            raise PackageInstallationError(
                f"npm init failed: {last_error or 'Unknown error'}"
            )

        except PackageInstallationError:
            raise
        except Exception as e:
            raise PackageInstallationError(f"Failed to initialize npm: {e}")

    def _use_cmd_npm(self) -> bool:
        """Check if we should use npm.cmd instead of npm (Windows compatibility)"""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            return result.returncode != 0
        except Exception:
            return True  # Default to .cmd on Windows if npm fails

    def _build_install_command(
        self,
        npm_cmd: str,
        packages: List[str],
        dev: bool,
        extra_flags: List[str] = None,
    ) -> List[str]:
        """Build npm install command with optional flags."""
        extra_flags = extra_flags or []
        cmd = [npm_cmd, "install"]
        if dev:
            cmd.append("--save-dev")
        cmd.extend(extra_flags)
        cmd.extend(packages)
        return cmd

    def _run_install_attempt(
        self,
        cmd: List[str],
        project_path: str,
        timeout_seconds: int = 180,
    ) -> subprocess.CompletedProcess:
        """Execute one npm install attempt."""
        return subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

    def _detect_retry_flag_sets(
        self,
        stderr: str,
        retry_with_ignore_scripts: bool,
    ) -> List[List[str]]:
        """Suggest retry flags based on npm error output."""
        lower = (stderr or "").lower()
        retry_flag_sets = [["--no-audit", "--no-fund"]]

        if ("gyp err!" in lower or "node-gyp" in lower) and retry_with_ignore_scripts:
            retry_flag_sets.insert(0, ["--ignore-scripts"])

        if "eresolve" in lower or "unable to resolve dependency tree" in lower:
            retry_flag_sets.append(["--legacy-peer-deps"])

        if any(token in lower for token in ["econnreset", "etimedout", "eai_again", "network"]):
            retry_flag_sets.append(["--prefer-online"])

        # De-duplicate exact flag sets while preserving order.
        unique_flag_sets = []
        seen = set()
        for flags in retry_flag_sets:
            key = tuple(flags)
            if key not in seen:
                unique_flag_sets.append(flags)
                seen.add(key)

        return unique_flag_sets

    def install_packages(
        self,
        project_path: str,
        packages: List[str],
        dev: bool = False,
        retry_with_ignore_scripts: bool = True,
    ) -> bool:
        """
        Install npm packages
        
        Args:
            project_path: Root project path
            packages: List of package names to install
            dev: If True, install as devDependencies
            retry_with_ignore_scripts: If True, retry with --ignore-scripts on failure
            
        Returns:
            True if successful
        """
        if not packages:
            return True

        try:
            packages = list(dict.fromkeys(packages))
            package_str = " ".join(packages)
            install_type = "devDependencies" if dev else "dependencies"

            self.logger.step(
                f"Installing {len(packages)} {install_type}: {package_str}"
            )

            npm_cmd = "npm.cmd" if self._use_cmd_npm() else "npm"
            cmd = self._build_install_command(npm_cmd, packages, dev)
            result = self._run_install_attempt(cmd, project_path, timeout_seconds=180)

            if result.returncode != 0:
                npm_error_summary = self._summarize_npm_stderr(result.stderr)
                self.logger.debug(f"npm install stderr:\n{result.stderr}")

                self.logger.warning(f"npm install failed: {npm_error_summary}")

                retry_flag_sets = self._detect_retry_flag_sets(
                    result.stderr,
                    retry_with_ignore_scripts,
                )

                # Retry whole batch with adaptive flags first.
                for flags in retry_flag_sets:
                    retry_cmd = self._build_install_command(
                        npm_cmd,
                        packages,
                        dev,
                        extra_flags=flags,
                    )
                    self.logger.warning(
                        f"Retrying install with flags: {' '.join(flags)}"
                    )

                    retry_result = self._run_install_attempt(
                        retry_cmd,
                        project_path,
                        timeout_seconds=240,
                    )

                    if retry_result.returncode == 0:
                        if "--ignore-scripts" in flags:
                            self.logger.success(
                                f"Successfully installed {len(packages)} {install_type} (build scripts skipped)"
                            )
                            self.logger.warning(
                                "Note: Native modules were installed without compilation. Install Visual Studio C++ build tools if native bindings are needed."
                            )
                        else:
                            self.logger.success(
                                f"Successfully installed {len(packages)} {install_type}"
                            )
                        return True

                    retry_error_summary = self._summarize_npm_stderr(
                        retry_result.stderr
                    )
                    self.logger.warning(f"Retry failed: {retry_error_summary}")
                    self.logger.debug(
                        f"Retry npm install stderr:\n{retry_result.stderr}"
                    )

                # If batch retries fail, install package-by-package to salvage what can be installed.
                self.logger.warning(
                    "Batch install still failing. Trying package-by-package to install remaining packages..."
                )
                per_package_flag_sets = [[]] + retry_flag_sets
                failed_packages = []
                installed_count = 0

                for pkg in packages:
                    pkg_installed = False
                    pkg_error_summary = "Unknown npm error"

                    for flags in per_package_flag_sets:
                        pkg_cmd = self._build_install_command(
                            npm_cmd,
                            [pkg],
                            dev,
                            extra_flags=flags,
                        )
                        pkg_result = self._run_install_attempt(
                            pkg_cmd,
                            project_path,
                            timeout_seconds=180,
                        )

                        if pkg_result.returncode == 0:
                            pkg_installed = True
                            installed_count += 1
                            break

                        pkg_error_summary = self._summarize_npm_stderr(
                            pkg_result.stderr
                        )

                    if not pkg_installed:
                        failed_packages.append(f"{pkg} ({pkg_error_summary})")

                if not failed_packages:
                    self.logger.success(
                        f"Successfully installed {len(packages)} {install_type} (package-by-package fallback)"
                    )
                    return True

                if installed_count == 0:
                    first_errors = "; ".join(failed_packages[:3])
                    suffix = "" if len(failed_packages) <= 3 else "; ..."
                    raise PackageInstallationError(
                        f"Package installation failed: {first_errors}{suffix}"
                    )

                skipped_names = ", ".join(
                    [item.split(" (")[0] for item in failed_packages[:8]]
                )
                if len(failed_packages) > 8:
                    skipped_names += ", ..."

                self.logger.warning(
                    f"Installed {installed_count}/{len(packages)} {install_type}. Skipped: {skipped_names}"
                )
                self.logger.warning(
                    "Continuing setup with installed packages only."
                )
                return True

            self.logger.success(
                f"Successfully installed {len(packages)} {install_type}"
            )
            return True

        except subprocess.TimeoutExpired:
            raise PackageInstallationError("Package installation timed out")
        except Exception as e:
            raise PackageInstallationError(f"Failed to install packages: {e}")

    def install_all_packages(
        self,
        project_path: str,
        dependencies: Dict[str, List[str]],
        dev_dependencies: Dict[str, List[str]],
    ) -> bool:
        """
        Install all dependencies and dev dependencies
        
        Args:
            project_path: Root project path
            dependencies: Dict with package lists {'prod': [...], 'dev': [...]}
            dev_dependencies: Dict with dev package lists
            
        Returns:
            True if all successful
        """
        try:
            all_prod_packages = []
            all_dev_packages = []

            # Flatten all packages
            for pkg_list in dependencies.values():
                all_prod_packages.extend(pkg_list)

            for pkg_list in dev_dependencies.values():
                all_dev_packages.extend(pkg_list)

            # Remove duplicates
            all_prod_packages = list(dict.fromkeys(all_prod_packages))
            all_dev_packages = [
                pkg for pkg in dict.fromkeys(all_dev_packages)
                if pkg not in all_prod_packages
            ]

            # Install production dependencies
            if all_prod_packages:
                self.install_packages(project_path, all_prod_packages, dev=False, retry_with_ignore_scripts=True)

            # Install dev dependencies
            if all_dev_packages:
                self.install_packages(project_path, all_dev_packages, dev=True, retry_with_ignore_scripts=True)

            return True

        except Exception as e:
            raise PackageInstallationError(f"Failed to install packages: {e}")

    def resolve_framework_packages(
        self, framework: str, config: Dict
    ) -> Tuple[List[str], List[str]]:
        """
        Resolve actual npm packages for a framework
        
        Args:
            framework: Framework name (react, next, etc.)
            config: Configuration dict with framework mappings
            
        Returns:
            Tuple of (packages, devDependencies)
        """
        # Search in all categories
        for category in ["frameworks", "styling", "databases", "utilities"]:
            if category in config:
                for key, details in config[category].items():
                    if key == framework.lower():
                        return (
                            details.get("packages", []),
                            details.get("devDependencies", []),
                        )

        # Unknown framework - return as-is (user custom input)
        return [framework], []

    def get_all_packages_for_selection(
        self, selections: Dict[str, List[str]], config: Dict
    ) -> Tuple[List[str], List[str]]:
        """
        Get all packages and devDependencies for user selections
        
        Args:
            selections: Dict with selected items  
            config: Configuration with framework mappings
            
        Returns:
            Tuple of (all_packages, all_dev_packages)
        """
        all_packages = []
        all_dev_packages = []

        # Process each category of selections
        for selection_list in selections.values():
            for item in selection_list:
                packages, dev_packages = self.resolve_framework_packages(
                    item, config
                )
                all_packages.extend(packages)
                all_dev_packages.extend(dev_packages)

        # Remove duplicates while preserving order
        all_packages = list(dict.fromkeys(all_packages))
        all_dev_packages = list(dict.fromkeys(all_dev_packages))

        return all_packages, all_dev_packages
