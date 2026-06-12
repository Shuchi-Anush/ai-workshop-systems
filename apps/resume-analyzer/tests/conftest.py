# This conftest allows pytest to discover fixtures/mocks inside apps/resume-analyzer/tests
import sys
import os

# Ensure the tests directory is in sys.path so we can import fixtures and mocks
sys.path.insert(0, os.path.dirname(__file__))
