"""
Error handling module for graceful error management.
Provides custom exceptions and error handling utilities.
"""

from typing import Optional


class ProjectSetupException(Exception):
    """Base exception for project setup errors"""

    pass


class ConfigurationError(ProjectSetupException):
    """Raised when configuration is invalid"""

    pass


class PackageInstallationError(ProjectSetupException):
    """Raised when package installation fails"""

    pass


class ProjectCreationError(ProjectSetupException):
    """Raised when project creation fails"""

    pass


class ValidationError(ProjectSetupException):
    """Raised when user input validation fails"""

    pass


class FileOperationError(ProjectSetupException):
    """Raised when file operations fail"""

    pass


class ErrorHandler:
    """Handles exceptions with detailed error messages"""

    @staticmethod
    def handle_exception(
        exception: Exception, logger, context: Optional[str] = None
    ) -> None:
        """
        Handle an exception with proper logging
        
        Args:
            exception: The exception to handle
            logger: Logger instance
            context: Additional context about the error
        """
        error_message = str(exception)

        if context:
            logger.error(f"{context}: {error_message}")
        else:
            logger.error(error_message)

        # Log different exception types with specific info
        if isinstance(exception, PackageInstallationError):
            lower_message = error_message.lower()
            if "npm init" in lower_message or "initialize npm" in lower_message:
                logger.warning(
                    "npm initialization failed. Check npm configuration and try again."
                )
            elif "install" in lower_message:
                logger.warning(
                    "Package installation failed. Check your npm/node installation."
                )
            else:
                logger.warning("npm setup step failed. Please review the error above.")

        elif isinstance(exception, ProjectCreationError):
            logger.warning("Failed to create project structure. Check disk space.")

        elif isinstance(exception, ConfigurationError):
            logger.warning("Configuration error. Check config.json is valid JSON.")

        elif isinstance(exception, ValidationError):
            logger.warning("Input validation failed. Please check your input and retry.")

    @staticmethod
    def safe_execute(
        func, logger, error_context: str = None, fallback_return=None
    ):
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            logger: Logger instance
            error_context: Context for error message
            fallback_return: Return value if function fails
            
        Returns:
            Result of func or fallback_return if error occurs
        """
        try:
            return func()
        except ProjectSetupException as e:
            ErrorHandler.handle_exception(e, logger, error_context)
            return fallback_return
        except Exception as e:
            ErrorHandler.handle_exception(e, logger, error_context or "Unexpected error")
            return fallback_return
