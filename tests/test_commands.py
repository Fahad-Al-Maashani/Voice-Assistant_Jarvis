#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Command Processing Tests
Author: Fahad Al Maashani
Description: Test suite for command processing and execution safety
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
import subprocess
import time

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from jarvis import JARVISConfig, SecurityManager, CommandProcessor, JARVISLogger
except ImportError as e:
    print(f"Error importing JARVIS modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class TestSecurityManager(unittest.TestCase):
    """Test the SecurityManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = JARVISConfig(self.temp_dir)
        self.logger = JARVISLogger(debug=True)
        self.security = SecurityManager(self.config, self.logger)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_allowed_commands(self):
        """Test that allowed commands pass validation"""
        allowed_commands = ["ls", "pwd", "cat", "head", "tail", "ps", "top"]
        
        for cmd in allowed_commands:
            with self.subTest(command=cmd):
                self.assertTrue(
