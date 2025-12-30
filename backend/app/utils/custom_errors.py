class ExtractionException(Exception):
    """Raises exception if text extraction from supported files failed"""

    def ___init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EmptyInputException(Exception):
    """Raises exception if the input is empty"""

    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(self.message)
