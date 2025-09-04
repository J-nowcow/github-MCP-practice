"""Test feature for PR testing."""

def hello_world():
    """Simple test function."""
    return "Hello from test feature!"

def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b

if __name__ == "__main__":
    print(hello_world())
    print(f"Sum: {calculate_sum(5, 3)}")
