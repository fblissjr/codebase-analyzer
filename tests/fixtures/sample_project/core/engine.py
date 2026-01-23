"""Engine module for processing."""

from utils.helpers import validate_input


class Engine:
    """Main processing engine."""

    def __init__(self):
        """Initialize the engine."""
        self.config = {}

    def process(self, data: str) -> dict:
        """Process input data.

        Args:
            data: Input string to process

        Returns:
            Processed result dictionary
        """
        if not validate_input(data):
            return {"error": "Invalid input"}

        return {
            "status": "success",
            "data": data.upper(),
            "length": len(data),
        }

    def configure(self, **kwargs):
        """Configure the engine."""
        self.config.update(kwargs)
