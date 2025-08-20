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
                    self.security.validate_command(cmd),
                    f"Command '{cmd}' should be allowed"
                )
    
    def test_validate_allowed_commands_with_args(self):
        """Test that allowed commands with arguments pass validation"""
        test_cases = [
            "ls -la",
            "ps aux",
            "cat /etc/hostname",
            "grep test",
            "find . -name test"
        ]
        
        for cmd in test_cases:
            with self.subTest(command=cmd):
                self.assertTrue(
                    self.security.validate_command(cmd),
                    f"Command '{cmd}' should be allowed"
                )
    
    def test_block_forbidden_commands(self):
        """Test that forbidden commands are blocked"""
        forbidden_commands = [
            "sudo ls",
            "su root",
            "rm -rf /",
            "chmod 777 /etc/passwd",
            "mkfs.ext4 /dev/sda1",
            "fdisk /dev/sda"
        ]
        
        for cmd in forbidden_commands:
            with self.subTest(command=cmd):
                self.assertFalse(
                    self.security.validate_command(cmd),
                    f"Command '{cmd}' should be blocked"
                )
    
    def test_block_unlisted_commands(self):
        """Test that commands not in whitelist are blocked"""
        unlisted_commands = [
            "netcat",
            "nc",
            "telnet",
            "ssh",
            "ftp",
            "unknown_command"
        ]
        
        for cmd in unlisted_commands:
            with self.subTest(command=cmd):
                self.assertFalse(
                    self.security.validate_command(cmd),
                    f"Unlisted command '{cmd}' should be blocked"
                )
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        test_cases = [
            ("ls -la", "ls -la"),  # Normal command
            ("ls; rm file", "ls rm file"),  # Remove semicolon
            ("ls && rm file", "ls  rm file"),  # Remove &&
            ("ls | grep test", "ls  grep test"),  # Remove pipe
            ("echo `whoami`", "echo whoami"),  # Remove backticks
            ("ls $HOME", "ls HOME"),  # Remove $
            ("cat /etc/passwd > file", "cat /etc/passwd  file")  # Remove >
        ]
        
        for input_cmd, expected in test_cases:
            with self.subTest(input=input_cmd):
                result = self.security.sanitize_input(input_cmd)
                self.assertEqual(
                    result, expected,
                    f"Sanitization failed for '{input_cmd}'"
                )

class TestCommandProcessor(unittest.TestCase):
    """Test the CommandProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = JARVISConfig(self.temp_dir)
        self.logger = JARVISLogger(debug=True)
        self.security = SecurityManager(self.config, self.logger)
        self.processor = CommandProcessor(self.config, self.logger, self.security)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_safe_command(self):
        """Test execution of safe commands"""
        result = self.processor.execute_command("pwd")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        self.assertTrue(len(result["output"]) > 0)
    
    def test_execute_command_with_output(self):
        """Test command execution with expected output"""
        result = self.processor.execute_command("echo test")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("test", result["output"])
    
    def test_block_unsafe_command(self):
        """Test that unsafe commands are blocked"""
        result = self.processor.execute_command("sudo rm -rf /")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not allowed", result["message"])
    
    def test_command_timeout(self):
        """Test command timeout functionality"""
        # Mock subprocess.run to simulate long-running command
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("sleep", 30)
            
            result = self.processor.execute_command("sleep 30")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("timed out", result["message"])
    
    def test_command_not_found(self):
        """Test handling of non-existent commands"""
        result = self.processor.execute_command("nonexistent_command_12345")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
    
    def test_output_size_limit(self):
        """Test output size limiting"""
        # Create a command that would generate large output
        large_output_cmd = "python3 -c 'print(\"x\" * 20000)'"
        
        # Since python3 might not be in whitelist, we'll mock the execution
        with patch.object(self.security, 'validate_command', return_value=True):
            with patch('subprocess.run') as mock_run:
                # Simulate large output
                large_output = "x" * 15000
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=large_output,
                    stderr=""
                )
                
                result = self.processor.execute_command(large_output_cmd)
                
                # Check that output was truncated
                self.assertTrue(len(result["output"]) <= self.config.security_config["max_output_size"])
                self.assertIn("truncated", result["output"])

class TestCommandIntegration(unittest.TestCase):
    """Integration tests for command processing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = JARVISConfig(self.temp_dir)
        self.logger = JARVISLogger(debug=True)
        self.security = SecurityManager(self.config, self.logger)
        self.processor = CommandProcessor(self.config, self.logger, self.security)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_system_commands(self):
        """Test file system related commands"""
        commands = [
            ("pwd", "should return current directory"),
            ("ls", "should list directory contents"),
            ("whoami", "should return current user")
        ]
        
        for cmd, description in commands:
            with self.subTest(command=cmd):
                result = self.processor.execute_command(cmd)
                self.assertEqual(
                    result["status"], "success",
                    f"{cmd} {description}"
                )
                self.assertTrue(
                    len(result["output"]) > 0,
                    f"{cmd} should produce output"
                )
    
    def test_system_info_commands(self):
        """Test system information commands"""
        commands = ["uname", "uptime", "df", "free"]
        
        for cmd in commands:
            with self.subTest(command=cmd):
                result = self.processor.execute_command(cmd)
                # These commands should work on most systems
                if result["status"] == "success":
                    self.assertTrue(len(result["output"]) > 0)
                else:
                    # If command fails, it should be handled gracefully
                    self.assertIn("status", result)
    
    def test_network_commands(self):
        """Test network related commands"""
        # Test ping (if network is available)
        result = self.processor.execute_command("ping -c 1 127.0.0.1")
        
        # Ping should either succeed or fail gracefully
        self.assertIn(result["status"], ["success", "error"])
        
        if result["status"] == "success":
            self.assertIn("output", result)
    
    def test_command_error_handling(self):
        """Test error handling for various scenarios"""
        test_cases = [
            ("ls /nonexistent/directory", "should handle file not found"),
            ("grep", "should handle missing arguments"),
            ("cat /dev/null", "should handle empty file")
        ]
        
        for cmd, description in test_cases:
            with self.subTest(command=cmd):
                result = self.processor.execute_command(cmd)
                # Should not crash, should return proper status
                self.assertIn("status", result)
                self.assertIn(result["status"], ["success", "error"])

class TestSecurityPatterns(unittest.TestCase):
    """Test security pattern detection"""
    
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
    
    def test_injection_attempts(self):
        """Test detection of command injection attempts"""
        injection_attempts = [
            "ls; rm -rf /",
            "ls && sudo reboot",
            "ls | sudo cat /etc/shadow",
            "ls `sudo whoami`",
            "ls $(sudo id)",
            "ls > /etc/passwd"
        ]
        
        for attempt in injection_attempts:
            with self.subTest(injection=attempt):
                # After sanitization, these should either be blocked or neutered
                sanitized = self.security.sanitize_input(attempt)
                self.assertFalse(
                    self.security.validate_command(sanitized),
                    f"Injection attempt should be blocked: {attempt}"
                )
    
    def test_privilege_escalation_attempts(self):
        """Test detection of privilege escalation attempts"""
        escalation_attempts = [
            "sudo ls",
            "su - root",
            "sudo -i",
            "sudo su",
            "pkexec ls",
            "doas ls"
        ]
        
        for attempt in escalation_attempts:
            with self.subTest(escalation=attempt):
                self.assertFalse(
                    self.security.validate_command(attempt),
                    f"Privilege escalation should be blocked: {attempt}"
                )
    
    def test_system_modification_attempts(self):
        """Test detection of system modification attempts"""
        modification_attempts = [
            "chmod 777 /etc",
            "chown root:root /etc/passwd",
            "rm -rf /",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/sda",
            "systemctl stop ssh"
        ]
        
        for attempt in modification_attempts:
            with self.subTest(modification=attempt):
                self.assertFalse(
                    self.security.validate_command(attempt),
                    f"System modification should be blocked: {attempt}"
                )

class TestConfigurationSecurity(unittest.TestCase):
    """Test configuration-based security"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_custom_allowed_commands(self):
        """Test custom allowed commands configuration"""
        # Create custom config
        config_file = os.path.join(self.temp_dir, "settings.json")
        custom_config = {
            "general": {"wake_word": "jarvis"},
            "security": {
                "allowed_commands": ["echo", "date"]  # Only these two
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(custom_config, f)
        
        # Create security manager with custom config
        config = JARVISConfig(self.temp_dir)
        # Override security config for this test
        config.security_config["allowed_commands"] = ["echo", "date"]
        
        logger = JARVISLogger(debug=True)
        security = SecurityManager(config, logger)
        
        # Test that only configured commands are allowed
        self.assertTrue(security.validate_command("echo"))
        self.assertTrue(security.validate_command("date"))
        self.assertFalse(security.validate_command("ls"))  # Not in custom list
        self.assertFalse(security.validate_command("pwd"))  # Not in custom list
    
    def test_timeout_configuration(self):
        """Test command timeout configuration"""
        config = JARVISConfig(self.temp_dir)
        config.security_config["max_execution_time"] = 1  # 1 second timeout
        
        logger = JARVISLogger(debug=True)
        security = SecurityManager(config, logger)
        processor = CommandProcessor(config, logger, security)
        
        # Test with a command that should timeout
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("sleep", 1)
            
            result = processor.execute_command("sleep 5")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("timed out", result["message"])

def run_command_tests():
    """Run all command processing tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSecurityManager,
        TestCommandProcessor,
        TestCommandIntegration,
        TestSecurityPatterns,
        TestConfigurationSecurity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 JARVIS Command Processing Tests")
    print("=" * 50)
    
    success = run_command_tests()
    
    if success:
        print("\n✅ All command tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some command tests failed!")
        sys.exit(1)
