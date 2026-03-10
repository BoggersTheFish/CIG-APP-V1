import pytest
import sys
import os

# Add python to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "tests/"]) if os.path.isdir("tests") else pytest.main(["-v"]))
