"""Sample entry point for testing."""

from core.engine import Engine
from utils.helpers import format_output


def main():
    """Main function."""
    engine = Engine()
    result = engine.process("test data")
    print(format_output(result))


if __name__ == "__main__":
    main()
