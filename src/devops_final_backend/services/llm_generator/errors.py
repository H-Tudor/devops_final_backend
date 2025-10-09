class LLMError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__()


class ModelFailedToRespond(LLMError):
    def __init__(self):
        super().__init__("The model failed to respond")


class InvalidModelParameters(LLMError):
    def __init__(self, params: list):
        super().__init__(f"The following parameters are missing: {', '.join(params)}")


class InvalidModelResponse(LLMError):
    def __init__(self, error: str):
        super().__init__(f"The response generated failed validation: {error}")


class ValidationError(LLMError):
    def __init__(self, message):
        super().__init__(message)
