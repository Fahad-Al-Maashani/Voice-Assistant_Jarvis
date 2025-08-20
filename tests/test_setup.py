def test_web_search_dependencies(self):
        """Test web search functionality dependencies"""
        try:
            import requests
            import googlesearch
            import wikipedia
            
            # Test basic HTTP request
            response = requests.get("https://httpbin.org/get", timeout=10)
            self.assertEqual(response.status_code, 200, "HTTP requests should work")
            
            # Test Wikipedia API
            try:
                summary = wikipedia.summary("Python programming", sentences=1)
                self.assertIsInstance(summary, str, "Wikipedia API should return string")
                self.assertGreater(len(summary), 0, "Wikipedia summary should not be empty")
            except Exception as e:
                self.skipTest(f"Wikipedia API test failed: {e}")
                
        except ImportError as e:
            self.fail(f"Web search dependencies missing: {e}")
        except requests.exceptions.RequestException:
            self.skipTest("Network request failed")

class TestFileSystemStructure(unittest.TestCase):
    """Test file system structure and permissions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def test_project_structure(self):
        """Test that required project files exist"""
        required_files = [
            "jarvis.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        required_dirs = [
            "config",
            "scripts",
            "tests",
            "docs"
        ]
        
        # Check files
        for file_name in required_files:
            file_path = os.path.join(self.project_root, file_name)
            self.assertTrue(
                os.path.exists(file_path),
                f"Required file {file_name} not found"
            )
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            self.assertTrue(
                os.path.exists(dir_path),
                f"Required directory {dir_name} not found"
            )
    
    def test_script_permissions(self):
        """Test that scripts have proper permissions"""
        script_files = [
            "scripts/install_dependencies.sh",
            "scripts/start_jarvis.sh",
            "scripts/test_audio.sh"
        ]
        
        for script in script_files:
            script_path = os.path.join(self.project_root, script)
            if os.path.exists(script_path):
                # Check if file is executable
                self.assertTrue(
                    os.access(script_path, os.X_OK),
                    f"Script {script} should be executable"
                )
    
    def test_log_directory_creation(self):
        """Test log directory creation and permissions"""
        logs_dir = os.path.join(self.project_root, "logs")
        
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        self.assertTrue(os.path.exists(logs_dir), "Logs directory should exist")
        self.assertTrue(os.access(logs_dir, os.W_OK), "Logs directory should be writable")
    
    def test_config_directory_structure(self):
        """Test configuration directory structure"""
        config_dir = os.path.join(self.project_root, "config")
        
        # Should be able to create config directory
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        self.assertTrue(os.path.exists(config_dir), "Config directory should exist")
        self.assertTrue(os.access(config_dir, os.R_OK), "Config directory should be readable")
        self.assertTrue(os.access(config_dir, os.W_OK), "Config directory should be writable")
    
    def test_requirements_file_validity(self):
        """Test that requirements.txt is valid"""
        requirements_file = os.path.join(self.project_root, "requirements.txt")
        
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as f:
                content = f.read()
                
                # Should contain key dependencies
                required_packages = [
                    "speech_recognition",
                    "pyttsx3",
                    "rich",
                    "requests"
                ]
                
                for package in required_packages:
                    self.assertIn(
                        package.lower(), content.lower(),
                        f"Required package {package} not found in requirements.txt"
                    )

class TestVirtualEnvironment(unittest.TestCase):
    """Test virtual environment setup"""
    
    def test_virtual_environment_detection(self):
        """Test virtual environment detection"""
        # Check if we're in a virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV') is not None
        )
        
        if not in_venv:
            self.skipTest("Not running in virtual environment")
        
        # Test virtual environment paths
        venv_path = sys.prefix
        self.assertTrue(os.path.exists(venv_path), "Virtual environment path should exist")
        
        # Check for virtual environment structure
        venv_bin = os.path.join(venv_path, "bin")
        venv_scripts = os.path.join(venv_path, "Scripts")  # Windows
        venv_lib = os.path.join(venv_path, "lib")
        
        self.assertTrue(
            os.path.exists(venv_bin) or os.path.exists(venv_scripts),
            "Virtual environment bin/Scripts directory should exist"
        )
        self.assertTrue(os.path.exists(venv_lib), "Virtual environment lib directory should exist")
    
    def test_pip_in_virtual_environment(self):
        """Test pip functionality in virtual environment"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(result.returncode, 0, "pip should be available")
            self.assertIn("pip", result.stdout.lower(), "Should show pip version")
            
        except subprocess.TimeoutExpired:
            self.fail("pip command timed out")
    
    def test_python_path_in_virtual_environment(self):
        """Test Python path in virtual environment"""
        # Check that Python executable is in virtual environment
        python_path = sys.executable
        
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # In virtual environment
            venv_path = sys.prefix
            self.assertTrue(
                python_path.startswith(venv_path),
                "Python executable should be in virtual environment"
            )

class TestSystemIntegration(unittest.TestCase):
    """Test system integration and compatibility"""
    
    def test_operating_system_compatibility(self):
        """Test operating system compatibility"""
        import platform
        
        system = platform.system().lower()
        self.assertIn(system, ["linux", "darwin", "windows"], "Unsupported operating system")
        
        if system == "linux":
            # Check for Ubuntu/Debian (preferred)
            try:
                with open("/etc/os-release", "r") as f:
                    os_info = f.read().lower()
                    is_ubuntu_debian = any(distro in os_info for distro in ["ubuntu", "debian", "mint"])
                    
                    if not is_ubuntu_debian:
                        self.skipTest("Non-Ubuntu/Debian Linux distribution detected")
                        
            except FileNotFoundError:
                self.skipTest("Cannot determine Linux distribution")
    
    def test_user_permissions(self):
        """Test user permissions and groups"""
        import pwd
        
        # Get current user info
        current_user = pwd.getpwuid(os.getuid()).pw_name
        
        # Check that user is not root
        self.assertNotEqual(current_user, "root", "Should not run as root user")
        
        # Check audio group membership (Linux only)
        if os.name == 'posix':
            try:
                import grp
                user_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]
                
                # Audio group membership is recommended but not required
                if "audio" not in user_groups:
                    self.skipTest("User not in audio group - may need: sudo usermod -a -G audio $USER")
                    
            except ImportError:
                self.skipTest("Cannot check group membership")
    
    def test_disk_space_availability(self):
        """Test available disk space"""
        import shutil
        
        # Check available disk space (at least 1GB)
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            
            self.assertGreater(free_gb, 1, "At least 1GB free disk space required")
            
        except OSError:
            # Try current directory on Windows
            try:
                total, used, free = shutil.disk_usage(".")
                free_gb = free / (1024**3)
                self.assertGreater(free_gb, 1, "At least 1GB free disk space required")
            except OSError:
                self.skipTest("Cannot determine disk space")
    
    def test_memory_availability(self):
        """Test available memory"""
        try:
            import psutil
            
            # Check available memory (at least 2GB total)
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            
            self.assertGreater(total_gb, 2, "At least 2GB total memory required")
            self.assertGreater(available_gb, 0.5, "At least 500MB available memory required")
            
        except ImportError:
            self.skipTest("psutil not available for memory check")
    
    def test_cpu_capabilities(self):
        """Test CPU capabilities"""
        import platform
        
        # Check CPU architecture
        machine = platform.machine().lower()
        supported_archs = ["x86_64", "amd64", "aarch64", "arm64"]
        
        self.assertIn(
            machine, supported_archs,
            f"Unsupported CPU architecture: {machine}"
        )
        
        # Check CPU count
        cpu_count = os.cpu_count()
        self.assertGreaterEqual(cpu_count, 1, "At least 1 CPU core required")
        
        if cpu_count == 1:
            self.skipTest("Single core CPU detected - performance may be limited")

class TestJARVISMainApplication(unittest.TestCase):
    """Test main JARVIS application functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_jarvis_import(self):
        """Test that JARVIS main module can be imported"""
        try:
            import jarvis
            self.assertTrue(hasattr(jarvis, "JARVIS"), "JARVIS class should be available")
            self.assertTrue(hasattr(jarvis, "main"), "main function should be available")
            
            # Test other important classes
            self.assertTrue(hasattr(jarvis, "JARVISConfig"), "JARVISConfig should be available")
            self.assertTrue(hasattr(jarvis, "SecurityManager"), "SecurityManager should be available")
            self.assertTrue(hasattr(jarvis, "VoiceEngine"), "VoiceEngine should be available")
            
        except ImportError as e:
            self.fail(f"Cannot import JARVIS module: {e}")
    
    def test_jarvis_initialization(self):
        """Test JARVIS initialization without starting main loop"""
        try:
            from jarvis import JARVIS
            
            # Initialize with test configuration
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test component initialization
            self.assertIsNotNone(jarvis_instance.config, "Config should be initialized")
            self.assertIsNotNone(jarvis_instance.logger, "Logger should be initialized")
            self.assertIsNotNone(jarvis_instance.security, "Security should be initialized")
            self.assertIsNotNone(jarvis_instance.commands, "Commands should be initialized")
            self.assertIsNotNone(jarvis_instance.web, "Web interface should be initialized")
            self.assertIsNotNone(jarvis_instance.ui, "UI manager should be initialized")
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
        except Exception as e:
            self.fail(f"JARVIS initialization failed: {e}")
    
    @patch('jarvis.VoiceEngine')
    def test_jarvis_with_mocked_voice(self, mock_voice):
        """Test JARVIS with mocked voice engine"""
        try:
            from jarvis import JARVIS
            
            # Mock voice engine to avoid audio requirements
            mock_voice_instance = Mock()
            mock_voice_instance.recognizer = Mock()
            mock_voice_instance.microphone = Mock()
            mock_voice_instance.tts_engine = Mock()
            mock_voice.return_value = mock_voice_instance
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test that voice engine was attempted to be initialized
            mock_voice.assert_called_once()
            
            # Test voice engine attributes
            self.assertIsNotNone(jarvis_instance.voice)
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_jarvis_signal_handling(self):
        """Test JARVIS signal handling"""
        try:
            from jarvis import JARVIS
            import signal
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test signal handler setup (should not raise exception)
            self.assertTrue(callable(jarvis_instance.signal_handler))
            
            # Test signal handler execution
            jarvis_instance.signal_handler(signal.SIGTERM, None)
            self.assertFalse(jarvis_instance.running)
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_jarvis_command_processing(self):
        """Test JARVIS command processing functionality"""
        try:
            from jarvis import JARVIS
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test basic command processing
            test_commands = [
                ("jarvis hello", True),  # Should process greeting
                ("jarvis help", True),   # Should process help
                ("hello world", True),   # Should ignore (no wake word)
            ]
            
            for command, expected_continue in test_commands:
                with self.subTest(command=command):
                    result = jarvis_instance.process_command(command)
                    self.assertIsInstance(result, bool)
                    
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestEnvironmentSetup(unittest.TestCase):
    """Test environment setup and configuration"""
    
    def test_environment_variables(self):
        """Test important environment variables"""
        # Check PATH
        path = os.environ.get('PATH', '')
        self.assertGreater(len(path), 0, "PATH environment variable should be set")
        
        # Check for Python in PATH
        python_paths = [p for p in path.split(os.pathsep) if 'python' in p.lower()]
        # Note: Python might be in standard locations even if not in PATH with 'python' in name
        
        # Check HOME directory
        home = os.environ.get('HOME') or os.environ.get('USERPROFILE')
        self.assertIsNotNone(home, "HOME/USERPROFILE should be set")
        self.assertTrue(os.path.exists(home), "Home directory should exist")
    
    def test_locale_settings(self):
        """Test locale settings"""
        import locale
        
        try:
            # Get current locale
            current_locale = locale.getlocale()
            self.assertIsNotNone(current_locale, "Locale should be set")
            
            # Test UTF-8 support
            test_string = "Hello 🤖 JARVIS"
            encoded = test_string.encode('utf-8')
            decoded = encoded.decode('utf-8')
            self.assertEqual(test_string, decoded, "UTF-8 encoding should work")
            
        except Exception as e:
            self.skipTest(f"Locale test failed: {e}")
    
    def test_shell_environment(self):
        """Test shell environment"""
        # Check SHELL variable (Unix-like systems)
        if os.name == 'posix':
            shell = os.environ.get('SHELL')
            if shell:
                self.assertTrue(os.path.exists(shell), "Shell should exist")
        
        # Check TERM variable (for terminal features)
        term = os.environ.get('TERM')
        if term:
            # Common terminal types
            common_terms = ['xterm', 'screen', 'tmux', 'linux', 'vt100']
            # Just verify it's a string (many valid values)
            self.assertIsInstance(term, str)

class TestDependencyVersions(unittest.TestCase):
    """Test dependency versions and compatibility"""
    
    def test_python_version_compatibility(self):
        """Test Python version compatibility"""
        version = sys.version_info
        
        # Python 3.8+
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 8)
        
        # Check for known incompatible versions
        if version.major == 3 and version.minor >= 12:
            # Python 3.12+ may have compatibility issues with some packages
            self.skipTest("Python 3.12+ detected - some packages may need updates")
    
    def test_critical_package_versions(self):
        """Test critical package versions"""
        critical_packages = {
            'speech_recognition': '3.8.0',
            'pyttsx3': '2.90',
            'rich': '13.0.0',
            'requests': '2.25.0'
        }
        
        for package_name, min_version in critical_packages.items():
            with self.subTest(package=package_name):
                try:
                    package = __import__(package_name)
                    
                    # Try to get version
                    version = getattr(package, '__version__', None)
                    if version:
                        # Simple version comparison (may need improvement for complex versions)
                        self.assertIsInstance(version, str, f"{package_name} version should be string")
                    
                except ImportError:
                    self.fail(f"Critical package {package_name} not available")
                except Exception as e:
                    self.skipTest(f"Version check failed for {package_name}: {e}")

def run_installation_tests():
    """Run all installation and setup tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes in order of dependency
    test_classes = [
        TestSystemRequirements,
        TestPythonDependencies,
        TestFileSystemStructure,
        TestVirtualEnvironment,
        TestJARVISConfiguration,
        TestJARVISComponents,
        TestAudioSystemIntegration,
        TestNetworkConnectivity,
        TestSystemIntegration,
        TestEnvironmentSetup,
        TestDependencyVersions,
        TestJARVISMainApplication
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def generate_system_report():
    """Generate a comprehensive system compatibility report"""
    print("\n" + "="*70)
    print("🔍 JARVIS COMPREHENSIVE SYSTEM COMPATIBILITY REPORT")
    print("="*70)
    
    import platform
    import subprocess
    
    # System information
    print(f"\n📊 System Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  CPU Cores: {os.cpu_count()}")
    print(f"  Platform: {platform.platform()}")
    
    # Memory information
    try:
        import psutil
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        print(f"  Memory: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available ({memory.percent:.1f}% used)")
        print(f"  Swap: {swap.total / (1024**3):.1f} GB total, {swap.free / (1024**3):.1f} GB free")
    except ImportError:
        print("  Memory: Unable to determine (psutil not available)")
    
    # Disk space
    import shutil
    try:
        total, used, free = shutil.disk_usage("/")
        print(f"  Disk Space: {free / (1024**3):.1f} GB free of {total / (1024**3):.1f} GB total ({(used/total)*100:.1f}% used)")
    except OSError:
        try:
            total, used, free = shutil.disk_usage(".")
            print(f"  Disk Space: {free / (1024**3):.1f} GB free of {total / (1024**3):.1f} GB total")
        except OSError:
            print("  Disk Space: Unable to determine")
    
    # Python environment
    print(f"\n🐍 Python Environment:")
    print(f"  Executable: {sys.executable}")
    print(f"  Version: {sys.version}")
    print(f"  Platform: {sys.platform}")
    
    # Virtual environment detection
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )
    print(f"  Virtual Environment: {'Yes' if in_venv else 'No'}")
    if in_venv:
        venv_path = os.environ.get('VIRTUAL_ENV', sys.prefix)
        print(f"  VEnv Path: {venv_path}")
    
    # Audio system
    print(f"\n🎤 Audio System:")
    try:
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=5)
        input_devices = result.stdout.count("card")
        print(f"  Input Devices: {input_devices}")
        
        # Show device details
        if input_devices > 0:
            lines = [line.strip() for line in result.stdout.split('\n') if 'card' in line]
            for line in lines[:3]:  # Show first 3 devices
                print(f"    {line}")
                
    except:
        print("  Input Devices: Unable to detect")
    
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
        output_devices = result.stdout.count("card")
        print(f"  Output Devices: {output_devices}")
    except:
        print("  Output Devices: Unable to detect")
    
    # PulseAudio
    try:
        subprocess.run(["pgrep", "pulseaudio"], capture_output=True, timeout=5, check=True)
        print("  PulseAudio: ✓ Running")
        
        # Get PulseAudio info
        try:
            result = subprocess.run(["pactl", "info"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Server Version' in line:
                        print(f"    Version: {line.split(':')[1].strip()}")
                        break
        except:
            pass
            
    except:
        print("  PulseAudio: ✗ Not running")
    
    # Network connectivity
    print(f"\n🌐 Network:")
    try:
        result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, timeout=10)
        if result.returncode == 0:
            print("  Internet: ✓ Connected")
            
            # Test DNS
            try:
                result = subprocess.run(["nslookup", "google.com"], capture_output=True, timeout=10)
                if result.returncode == 0:
                    print("  DNS: ✓ Working")
                else:
                    print("  DNS: ✗ Issues detected")
            except:
                print("  DNS: Unable to test")
                
        else:
            print("  Internet: ✗ Not connected")
    except:
        print("  Internet: Unable to test")
    
    # Python modules
    print(f"\n🐍 Python Dependencies:")
    required_modules = [
        ("speech_recognition", "Speech Recognition"),
        ("pyttsx3", "Text-to-Speech"),
        ("rich", "Rich Terminal UI"),
        ("requests", "HTTP Requests"),
        ("googlesearch", "Google Search"),
        ("wikipedia", "Wikipedia API"),
        ("psutil", "System Information"),
        ("pyaudio", "Audio I/O")
    ]
    
    available_count = 0
    for module_name, description in required_modules:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f"  ✓ {description} ({module_name}) - v{version}")
            available_count += 1
        except ImportError:
            print(f"  ✗ {description} ({module_name}) - Not installed")
    
    print(f"\n  Summary: {available_count}/{len(required_modules)} modules available")
    
    # System tools
    print(f"\n🛠️  System Tools:")
    tools = [
        ("git", "Version Control"),
        ("curl", "HTTP Client"),
        ("wget", "File Downloader"),
        ("espeak", "Text-to-Speech"),
        ("festival", "TTS Engine"),
        ("arecord", "Audio Recording"),
        ("aplay", "Audio Playback"),
        ("pactl", "PulseAudio Control")
    ]
    
    available_tools = 0
    for tool, description in tools:
        try:
            result = subprocess.run([tool, "--help"], capture_output=True, timeout=5)
            if result.returncode in [0, 1, 2]:  # Many tools return 1 or 2 for --help
                print(f"  ✓ {description} ({tool})")
                available_tools += 1
            else:
                print(f"  ✗ {description} ({tool}) - Not working")
        except:
            print(f"  ✗ {description} ({tool}) - Not found")
    
    print(f"\n  Summary: {available_tools}/{len(tools)} tools available")
    
    # Security check
    print(f"\n🔒 Security:")
    import pwd
    current_user = pwd.getpwuid(os.getuid()).pw_name
    print(f"  Current User: {current_user}")
    print(f"  Root Access: {'✗ Running as root (NOT RECOMMENDED)' if current_user == 'root' else '✓ Not running as root'}")
    
    try:
        import grp
        user_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]
        audio_group = "✓ Yes" if "audio" in user_groups else "✗ No (recommended: sudo usermod -a -G audio $USER)"
        print(f"  Audio Group: {audio_group}")
    except:
        print("  Audio Group: Unable to check")
    
    # Overall assessment
    print(f"\n📋 Overall Assessment:")
    score = 0
    max_score = 6
    
    # Check critical components
    if available_count >= len(required_modules) * 0.8:  # 80% of modules
        score += 1
        print("  ✓ Python dependencies mostly satisfied")
    else:
        print("  ✗ Missing critical Python dependencies")
    
    if available_tools >= len(tools) * 0.6:  # 60% of tools
        score += 1
        print("  ✓ System tools mostly available")
    else:
        print("  ✗ Missing important system tools")
    
    # Memory check
    try:
        import psutil
        if psutil.virtual_memory().total >= 2 * (1024**3):  # 2GB
            score += 1
            print("  ✓ Sufficient memory available")
        else:
            print("  ⚠️  Low memory (minimum 2GB recommended)")
    except:
        print("  ? Memory status unknown")
    
    # Disk space check
    try:
        _, _, free = shutil.disk_usage("/")
        if free >= 1 * (1024**3):  # 1GB
            score += 1
            print("  ✓ Sufficient disk space")
        else:
            print("  ⚠️  Low disk space (minimum 1GB free required)")
    except:
        print("  ? Disk space status unknown")
    
    # Audio check
    try:
        subprocess.run(["arecord", "-l"], capture_output=True, timeout=5, check=True)
        score += 1
        print("  ✓ Audio input devices detected")
    except:
        print("  ⚠️  No audio input devices detected")
    
    # Network check
    try:
        subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, timeout=10, check=True)
        score += 1
        print("  ✓ Internet connectivity working")
    except:
        print("  ⚠️  Internet connectivity issues")
    
    # Final assessment
    print(f"\n🎯 Compatibility Score: {score}/{max_score}")
    
    if score >= 5:
        print("  🎉 Excellent! Your system is ready for JARVIS!")
    elif score >= 4:
        print("  👍 Good! Minor issues may need attention.")
    elif score#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Setup and Installation Tests
Author: Fahad Al Maashani
Description: Test suite for JARVIS installation and system setup
"""

import unittest
import sys
import os
import tempfile
import subprocess
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSystemRequirements(unittest.TestCase):
    """Test system requirements and dependencies"""
    
    def test_python_version(self):
        """Test Python version requirement (3.8+)"""
        version_info = sys.version_info
        self.assertGreaterEqual(
            version_info.major, 3,
            "Python 3 is required"
        )
        self.assertGreaterEqual(
            version_info.minor, 8,
            "Python 3.8+ is required"
        )
    
    def test_required_system_commands(self):
        """Test that required system commands are available"""
        required_commands = [
            "python3",
            "pip3",
            "arecord",
            "aplay",
            "espeak"
        ]
        
        missing_commands = []
        for cmd in required_commands:
            try:
                subprocess.run([cmd, "--help"], 
                             capture_output=True, 
                             timeout=5)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_commands.append(cmd)
        
        if missing_commands:
            self.fail(f"Missing required commands: {', '.join(missing_commands)}")
    
    def test_audio_system_availability(self):
        """Test audio system availability"""
        # Check for audio devices
        try:
            # Test audio recording capability
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(result.returncode, 0, "arecord should be available")
            
            # Test audio playback capability
            result = subprocess.run(
                ["aplay", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.assertEqual(result.returncode, 0, "aplay should be available")
            
        except subprocess.TimeoutExpired:
            self.fail("Audio system commands timed out")
        except FileNotFoundError:
            self.fail("Audio system commands not found")

class TestPythonDependencies(unittest.TestCase):
    """Test Python module dependencies"""
    
    def test_core_modules(self):
        """Test that core Python modules can be imported"""
        core_modules = [
            "json",
            "os",
            "sys",
            "time",
            "threading",
            "subprocess",
            "signal",
            "logging",
            "pathlib"
        ]
        
        for module in core_modules:
            with self.subTest(module=module):
                try:
                    __import__(module)
                except ImportError:
                    self.fail(f"Core module {module} not available")
    
    def test_third_party_modules(self):
        """Test that required third-party modules can be imported"""
        third_party_modules = [
            "speech_recognition",
            "pyttsx3",
            "requests",
            "rich",
            "googlesearch",
            "wikipedia",
            "psutil"
        ]
        
        missing_modules = []
        for module in third_party_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            self.fail(f"Missing required modules: {', '.join(missing_modules)}")
    
    def test_audio_modules(self):
        """Test audio-related Python modules"""
        try:
            import pyaudio
        except ImportError:
            self.skipTest("pyaudio not available - may require system packages")
        
        # Test basic pyaudio functionality
        try:
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            p.terminate()
            self.assertGreater(device_count, 0, "No audio devices found")
        except Exception as e:
            self.fail(f"PyAudio initialization failed: {e}")

class TestJARVISConfiguration(unittest.TestCase):
    """Test JARVIS configuration system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration_creation(self):
        """Test that default configuration is created properly"""
        try:
            from jarvis import JARVISConfig
            config = JARVISConfig(self.config_dir)
            
            # Test that configuration has required sections
            self.assertIn("general", config.settings)
            self.assertIn("voice", config.settings)
            self.assertIn("ui", config.settings)
            
            # Test required configuration values
            self.assertIn("wake_word", config.settings["general"])
            self.assertIn("input", config.settings["voice"])
            self.assertIn("output", config.settings["voice"])
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_configuration_file_creation(self):
        """Test that configuration files are created correctly"""
        try:
            from jarvis import JARVISConfig
            config = JARVISConfig(self.config_dir)
            
            # Check that settings file exists
            settings_file = os.path.join(self.config_dir, "settings.json")
            self.assertTrue(os.path.exists(settings_file), "Settings file should be created")
            
            # Verify file is valid JSON
            with open(settings_file, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, dict, "Settings should be valid JSON object")
                
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestJARVISComponents(unittest.TestCase):
    """Test JARVIS component initialization"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """Test logger component initialization"""
        try:
            from jarvis import JARVISLogger
            logger = JARVISLogger(log_dir=self.logs_dir, debug=True)
            
            # Test logging methods
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            logger.debug("Test debug message")
            
            # Check that log file is created
            log_files = list(Path(self.logs_dir).glob("jarvis_*.log"))
            self.assertGreater(len(log_files), 0, "Log file should be created")
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_config_manager_initialization(self):
        """Test configuration manager initialization"""
        try:
            from jarvis import JARVISConfig
            config = JARVISConfig(self.config_dir)
            
            # Test configuration attributes
            self.assertIsInstance(config.settings, dict)
            self.assertIsInstance(config.audio_config, dict)
            self.assertIsInstance(config.security_config, dict)
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_security_manager_initialization(self):
        """Test security manager initialization"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, SecurityManager
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(log_dir=self.logs_dir, debug=True)
            security = SecurityManager(config, logger)
            
            # Test security attributes
            self.assertIsInstance(security.allowed_commands, set)
            self.assertIsInstance(security.forbidden_patterns, list)
            
            # Test basic validation
            self.assertTrue(security.validate_command("ls"))
            self.assertFalse(security.validate_command("sudo rm -rf /"))
            
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestAudioSystemIntegration(unittest.TestCase):
    """Test audio system integration"""
    
    def test_pulseaudio_running(self):
        """Test that PulseAudio is running"""
        try:
            result = subprocess.run(
                ["pgrep", "pulseaudio"],
                capture_output=True,
                timeout=5
            )
            self.assertEqual(result.returncode, 0, "PulseAudio should be running")
        except subprocess.TimeoutExpired:
            self.fail("pgrep command timed out")
        except FileNotFoundError:
            self.skipTest("pgrep not available")
    
    def test_audio_devices_detected(self):
        """Test that audio devices are detected"""
        try:
            # Check input devices
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "card" in result.stdout:
                # Input devices found
                pass
            else:
                self.skipTest("No audio input devices detected")
            
            # Check output devices
            result = subprocess.run(
                ["aplay", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "card" in result.stdout:
                # Output devices found
                pass
            else:
                self.skipTest("No audio output devices detected")
                
        except subprocess.TimeoutExpired:
            self.fail("Audio device detection timed out")
        except FileNotFoundError:
            self.skipTest("Audio tools not available")
    
    def test_text_to_speech_available(self):
        """Test that text-to-speech is available"""
        tts_engines = ["espeak", "festival", "spd-say"]
        
        working_engines = []
        for engine in tts_engines:
            try:
                result = subprocess.run(
                    [engine, "--help"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    working_engines.append(engine)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        self.assertGreater(
            len(working_engines), 0,
            "At least one TTS engine should be available"
        )

class TestNetworkConnectivity(unittest.TestCase):
    """Test network connectivity for web features"""
    
    def test_internet_connectivity(self):
        """Test basic internet connectivity"""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.skipTest("No internet connectivity")
                
        except subprocess.TimeoutExpired:
            self.skipTest("Ping timed out")
        except FileNotFoundError:
            self.skipTest("ping not available")
    
    def test_dns_resolution(self):
        """Test DNS resolution"""
        try:
            result = subprocess.run(
                ["nslookup", "google.com"],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.skipTest("DNS resolution failed")
                
        except subprocess.TimeoutExpired:
            self.skipTest("DNS lookup timed out")
        except FileNotFoundError:
            self.skipTest("nslookup not available")
    
    def test_web_search_dependencies(self):
        """Test web search functionality dependencies"""
        try:
            import requests
            import googlesearch
            import wikipedia
            
            # Test basic HTTP request
            response = requests.get("https://httpbin.org/get", timeout=10)
            self.assertEqual(response.status_code, 200, "HTTP requests should work")
            
            # Test Wikipedia API
            try:
                summary = wikipedia.summary("Python programming", sentences=1)
                self.assertIsInstance(summary, str, "Wikipedia API should return string")
                self.assertGreater(len(summary), 0, "Wikipedia summary should not be empty")
            except Exception as e:
                self.skipTest(f"Wikipedia API test failed: {e}")
                
        except ImportError as e:
            self.fail(f"Web search dependencies missing: {e}")
        except requests.exceptions.RequestException:
            self.skipTest("Network request failed")

class TestFileSystemStructure(unittest.TestCase):
    """Test file system structure and permissions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def test_project_structure(self):
        """Test that required project files exist"""
        required_files = [
            "jarvis.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        required_dirs = [
            "config",
            "scripts",
            "tests",
            "docs"
        ]
        
        # Check files
        for file_name in required_files:
            file_path = os.path.join(self.project_root, file_name)
            self.assertTrue(
                os.path.exists(file_path),
                f"Required file {file_name} not found"
            )
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            self.assertTrue(
                os.path.exists(dir_path),
                f"Required directory {dir_name} not found"
            )
    
    def test_script_permissions(self):
        """Test that scripts have proper permissions"""
        script_files = [
            "scripts/install_dependencies.sh",
            "scripts/start_jarvis.sh",
            "scripts/test_audio.sh"
        ]
        
        for script in script_files:
            script_path = os.path.join(self.project_root, script)
            if os.path.exists(script_path):
                # Check if file is executable
                self.assertTrue(
                    os.access(script_path, os.X_OK),
                    f"Script {script} should be executable"
                )
    
    def test_log_directory_creation(self):
        """Test log directory creation and permissions"""
        logs_dir = os.path.join(self.project_root, "logs")
        
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        self.assertTrue(os.path.exists(logs_dir), "Logs directory should exist")
        self.assertTrue(os.access(logs_dir, os.W_OK), "Logs directory should be writable")

class TestVirtualEnvironment(unittest.TestCase):
    """Test virtual environment setup"""
    
    def test_virtual_environment_detection(self):
        """Test virtual environment detection"""
        # Check if we're in a virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if not in_venv:
            self.skipTest("Not running in virtual environment")
        
        # Test virtual environment paths
        venv_path = sys.prefix
        self.assertTrue(os.path.exists(venv_path), "Virtual environment path should exist")
        
        # Check for virtual environment structure
        venv_bin = os.path.join(venv_path, "bin")
        venv_lib = os.path.join(venv_path, "lib")
        
        self.assertTrue(
            os.path.exists(venv_bin) or os.path.exists(os.path.join(venv_path, "Scripts")),
            "Virtual environment bin/Scripts directory should exist"
        )
        self.assertTrue(os.path.exists(venv_lib), "Virtual environment lib directory should exist")

class TestSystemIntegration(unittest.TestCase):
    """Test system integration and compatibility"""
    
    def test_operating_system_compatibility(self):
        """Test operating system compatibility"""
        import platform
        
        system = platform.system().lower()
        self.assertIn(system, ["linux", "darwin"], "JARVIS requires Linux or macOS")
        
        if system == "linux":
            # Check for Ubuntu/Debian
            try:
                with open("/etc/os-release", "r") as f:
                    os_info = f.read().lower()
                    self.assertTrue(
                        "ubuntu" in os_info or "debian" in os_info,
                        "Linux distribution should be Ubuntu or Debian-based"
                    )
            except FileNotFoundError:
                self.skipTest("Cannot determine Linux distribution")
    
    def test_user_permissions(self):
        """Test user permissions and groups"""
        import grp
        import pwd
        
        # Get current user info
        current_user = pwd.getpwuid(os.getuid()).pw_name
        user_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]
        
        # Check for audio group membership
        self.assertIn("audio", user_groups, "User should be in audio group")
    
    def test_disk_space_availability(self):
        """Test available disk space"""
        import shutil
        
        # Check available disk space (at least 1GB)
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        
        self.assertGreater(free_gb, 1, "At least 1GB free disk space required")
    
    def test_memory_availability(self):
        """Test available memory"""
        try:
            import psutil
            
            # Check available memory (at least 2GB total)
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            
            self.assertGreater(total_gb, 2, "At least 2GB total memory required")
            
        except ImportError:
            self.skipTest("psutil not available for memory check")

class TestJARVISMainApplication(unittest.TestCase):
    """Test main JARVIS application functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_jarvis_import(self):
        """Test that JARVIS main module can be imported"""
        try:
            import jarvis
            self.assertTrue(hasattr(jarvis, "JARVIS"), "JARVIS class should be available")
            self.assertTrue(hasattr(jarvis, "main"), "main function should be available")
        except ImportError as e:
            self.fail(f"Cannot import JARVIS module: {e}")
    
    def test_jarvis_initialization(self):
        """Test JARVIS initialization without starting main loop"""
        try:
            from jarvis import JARVIS
            
            # Initialize with test configuration
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test component initialization
            self.assertIsNotNone(jarvis_instance.config, "Config should be initialized")
            self.assertIsNotNone(jarvis_instance.logger, "Logger should be initialized")
            self.assertIsNotNone(jarvis_instance.security, "Security should be initialized")
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
        except Exception as e:
            self.fail(f"JARVIS initialization failed: {e}")
    
    @patch('jarvis.VoiceEngine')
    def test_jarvis_with_mocked_voice(self, mock_voice):
        """Test JARVIS with mocked voice engine"""
        try:
            from jarvis import JARVIS
            
            # Mock voice engine to avoid audio requirements
            mock_voice_instance = Mock()
            mock_voice.return_value = mock_voice_instance
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test that voice engine was attempted to be initialized
            mock_voice.assert_called_once()
            
        except ImportError:
            self.skipTest("JARVIS modules not available")

def run_installation_tests():
    """Run all installation and setup tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes in order of dependency
    test_classes = [
        TestSystemRequirements,
        TestPythonDependencies,
        TestFileSystemStructure,
        TestVirtualEnvironment,
        TestJARVISConfiguration,
        TestJARVISComponents,
        TestAudioSystemIntegration,
        TestNetworkConnectivity,
        TestSystemIntegration,
        TestJARVISMainApplication
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def generate_system_report():
    """Generate a system compatibility report"""
    print("\n" + "="*60)
    print("🔍 JARVIS SYSTEM COMPATIBILITY REPORT")
    print("="*60)
    
    import platform
    import subprocess
    
    # System information
    print(f"\n📊 System Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  CPU Cores: {os.cpu_count()}")
    
    # Memory information
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"  Memory: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available")
    except ImportError:
        print("  Memory: Unable to determine (psutil not available)")
    
    # Disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    print(f"  Disk Space: {free / (1024**3):.1f} GB free of {total / (1024**3):.1f} GB total")
    
    # Audio system
    print(f"\n🎤 Audio System:")
    try:
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=5)
        input_devices = result.stdout.count("card")
        print(f"  Input Devices: {input_devices}")
    except:
        print("  Input Devices: Unable to detect")
    
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
        output_devices = result.stdout.count("card")
        print(f"  Output Devices: {output_devices}")
    except:
        print("  Output Devices: Unable to detect")
    
    # PulseAudio
    try:
        subprocess.run(["pgrep", "pulseaudio"], capture_output=True, timeout=5, check=True)
        print("  PulseAudio: Running")
    except:
        print("  PulseAudio: Not running")
    
    # Network connectivity
    print(f"\n🌐 Network:")
    try:
        subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, timeout=10, check=True)
        print("  Internet: Connected")
    except:
        print("  Internet: Not connected")
    
    # Python modules
    print(f"\n🐍 Python Dependencies:")
    required_modules = [
        "speech_recognition", "pyttsx3", "rich", "requests", 
        "googlesearch", "wikipedia", "psutil"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🧪 JARVIS Setup and Installation Tests")
    print("=" * 50)
    
    # Generate system report first
    generate_system_report()
    
    # Run tests
    success = run_installation_tests()
    
    if success:
        print("\n✅ All setup tests passed!")
        print("🚀 Your system is ready for JARVIS!")
        sys.exit(0)
    else:
        print("\n❌ Some setup tests failed!")
        print("🔧 Please fix the issues above before running JARVIS.")
        sys.exit(1)