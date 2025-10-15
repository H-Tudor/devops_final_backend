class LLMError(Exception):
    """Base Exception for LLM Generator module related erros.

    This ensures all erros have a message attribute that can be used with the
    FastAPI Error-Catcher
    """

    def __init__(self, message: str):
        """Init the error with a string message

        Args:
            message (str): Pre-formated description of the error case
        """
        self.message = message
        super().__init__()


class ModelFailedToRespond(LLMError):
    """Raised when a response could not be obtained from the model

    Reasons include
    - model api is down
    - model api auth failed
    - something went wrong with the generation
    """

    def __init__(self):
        """Init with preformated message"""
        super().__init__("The model failed to respond")


class InvalidModelParameters(LLMError):
    """Raised when pre-generation params validation fails (like missing variables required by templates)"""

    def __init__(self, params: list):
        """Explicitly show the missing params

        Args:
            params (list[str]): the missing params as found by the validation function
        """
        super().__init__(f"The following parameters are missing: {', '.join(params)}")


class InvalidModelResponse(LLMError):
    """Raised when a propper message could not be generated despite a retry"""

    def __init__(self, error: str):
        """Init with a pre-formated error description

        Args:
            error (str): the error message produced by the validation function
        """
        super().__init__(f"Overall response generation failed: {error}")


class ValidationError(LLMError):
    """Raised during post-generation response validation if individual conditions are not met."""

    def __init__(self, error: str):
        """Init with a pre-formated error description

        Args:
            error (str): the error message produced by the validation function
        """
        super().__init__(f"The response generated failed validation: {error}")
