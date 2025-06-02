class GameError(Exception):
    """Base exception for game-related errors"""
    def __init__(self, message="A game error occurred"):
        self.message = message
        super().__init__(self.message)

class ValidationError(Exception):
    """Exception raised for validation errors"""
    def __init__(self, message="Validation error occurred"):
        self.message = message
        super().__init__(self.message) 