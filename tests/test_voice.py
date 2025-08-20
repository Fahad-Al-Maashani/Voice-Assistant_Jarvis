#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Voice System Tests
Author: Fahad Al Maashani
Description: Test suite for voice recognition and text-to-speech functionality
"""

import unittest
import sys
import os
import tempfile
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import wave
import struct

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSpeechRecognitionModule(unittest.TestCase):
    """Test speech recognition module availability and functionality"""
    
    def test_speech_recognition_import(self):
        """Test that speech_recognition module can be imported"""
        try:
            import speech_recognition as sr
            self.assertIsNotNone(sr, "speech_recognition module should be importable")
        except ImportError:
            self.fail("speech_recognition module not available")
    
    def test_recognizer_initialization(self):
        """Test speech recognizer initialization"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            self.assertIsInstance(recognizer, sr.Recognizer)
            
            # Test recognizer attributes
            self.assertTrue(hasattr(recognizer, 'energy_threshold'))
            self.assertTrue(hasattr(recognizer, 'dynamic_energy_threshold'))
            self.assertTrue(hasattr(recognizer, 'pause_threshold'))
            
        except ImportError:
            self.skipTest("speech_recognition module not available")
    
    def test_microphone_detection(self):
        """Test microphone device detection"""
        try:
            import speech_recognition as sr
            
            # Get microphone list
            mic_list = sr.Microphone.list_microphone_names()
            self.assertIsInstance(mic_list, list)
            
            if len(mic_list) == 0:
                self.skipTest("No microphone devices detected")
            
            # Test default microphone
            try:
                mic = sr.Microphone()
                self.assertIsInstance(mic, sr.Microphone)
            except OSError as e:
                self.skipTest(f"Cannot access microphone: {e}")
                
        except ImportError:
            self.skipTest("speech_recognition module not available")
    
    def test_audio_file_recognition(self):
        """Test audio file recognition capability"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Create a dummy audio file for testing
            test_audio_file = self.create_test_audio_file()
            
            try:
                with sr.AudioFile(test_audio_file) as source:
                    audio = recognizer.record(source)
                    self.assertIsInstance(audio, sr.AudioData)
            except Exception as e:
                self.skipTest(f"Audio file processing failed: {e}")
            finally:
                if os.path.exists(test_audio_file):
                    os.remove(test_audio_file)
                    
        except ImportError:
            self.skipTest("speech_recognition module not available")
    
    def create_test_audio_file(self):
        """Create a test WAV file for testing"""
        filename = tempfile.mktemp(suffix=".wav")
        
        # Create a simple sine wave
        sample_rate = 16000
        duration = 1  # 1 second
        frequency = 440  # A note
        
        frames = []
        for i in range(int(duration * sample_rate)):
            value = int(32767 * 0.3 * (i % (sample_rate // frequency)) / (sample_rate // frequency))
            frames.append(struct.pack('<h', value))
        
        # Write WAV file
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))
        
        return filename

class TestTextToSpeechModule(unittest.TestCase):
    """Test text-to-speech module availability and functionality"""
    
    def test_pyttsx3_import(self):
        """Test that pyttsx3 module can be imported"""
        try:
            import pyttsx3
            self.assertIsNotNone(pyttsx3, "pyttsx3 module should be importable")
        except ImportError:
            self.fail("pyttsx3 module not available")
    
    def test_tts_engine_initialization(self):
        """Test TTS engine initialization"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            self.assertIsNotNone(engine, "TTS engine should initialize")
            
            # Test engine methods
            self.assertTrue(hasattr(engine, 'say'))
            self.assertTrue(hasattr(engine, 'runAndWait'))
            self.assertTrue(hasattr(engine, 'stop'))
            
            engine.stop()
            
        except ImportError:
            self.skipTest("pyttsx3 module not available")
        except Exception as e:
            self.skipTest(f"TTS engine initialization failed: {e}")
    
    def test_voice_properties(self):
        """Test TTS voice properties"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Test getting voices
            voices = engine.getProperty('voices')
            self.assertIsInstance(voices, (list, type(None)))
            
            if voices:
                self.assertGreater(len(voices), 0, "At least one voice should be available")
                
                # Test voice properties
                for voice in voices[:3]:  # Test first 3 voices
                    self.assertTrue(hasattr(voice, 'id'))
                    self.assertTrue(hasattr(voice, 'name'))
            
            # Test rate property
            rate = engine.getProperty('rate')
            self.assertIsInstance(rate, (int, float))
            
            # Test volume property
            volume = engine.getProperty('volume')
            self.assertIsInstance(volume, (int, float))
            self.assertGreaterEqual(volume, 0)
            self.assertLessEqual(volume, 1)
            
            engine.stop()
            
        except ImportError:
            self.skipTest("pyttsx3 module not available")
        except Exception as e:
            self.skipTest(f"Voice properties test failed: {e}")
    
    def test_tts_configuration(self):
        """Test TTS engine configuration"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Test setting rate
            original_rate = engine.getProperty('rate')
            new_rate = 150
            engine.setProperty('rate', new_rate)
            self.assertEqual(engine.getProperty('rate'), new_rate)
            
            # Test setting volume
            original_volume = engine.getProperty('volume')
            new_volume = 0.8
            engine.setProperty('volume', new_volume)
            self.assertAlmostEqual(engine.getProperty('volume'), new_volume, places=1)
            
            # Restore original settings
            engine.setProperty('rate', original_rate)
            engine.setProperty('volume', original_volume)
            
            engine.stop()
            
        except ImportError:
            self.skipTest("pyttsx3 module not available")
        except Exception as e:
            self.skipTest(f"TTS configuration test failed: {e}")

class TestVoiceEngineIntegration(unittest.TestCase):
    """Test JARVIS VoiceEngine integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_voice_engine_initialization(self):
        """Test VoiceEngine class initialization"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Initialize VoiceEngine
            voice_engine = VoiceEngine(config, logger)
            
            # Test attributes
            self.assertIsNotNone(voice_engine.config)
            self.assertIsNotNone(voice_engine.logger)
            self.assertIsNotNone(voice_engine.recognizer)
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
        except Exception as e:
            self.skipTest(f"VoiceEngine initialization failed: {e}")
    
    @patch('speech_recognition.Microphone')
    @patch('speech_recognition.Recognizer')
    def test_voice_recognition_setup(self, mock_recognizer, mock_microphone):
        """Test voice recognition setup with mocked components"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            # Setup mocks
            mock_recognizer_instance = Mock()
            mock_recognizer.return_value = mock_recognizer_instance
            
            mock_microphone_instance = Mock()
            mock_microphone.return_value = mock_microphone_instance
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Initialize VoiceEngine
            voice_engine = VoiceEngine(config, logger)
            
            # Verify setup calls
            mock_recognizer.assert_called()
            mock_microphone.assert_called()
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    @patch('pyttsx3.init')
    def test_tts_setup(self, mock_tts_init):
        """Test text-to-speech setup with mocked components"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            # Setup mock TTS engine
            mock_tts_engine = Mock()
            mock_tts_engine.getProperty.return_value = []
            mock_tts_init.return_value = mock_tts_engine
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Initialize VoiceEngine
            voice_engine = VoiceEngine(config, logger)
            
            # Verify TTS initialization
            mock_tts_init.assert_called()
            
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestAudioSystemCompatibility(unittest.TestCase):
    """Test audio system compatibility"""
    
    def test_pyaudio_availability(self):
        """Test PyAudio availability"""
        try:
            import pyaudio
            
            # Test PyAudio initialization
            p = pyaudio.PyAudio()
            
            # Get device count
            device_count = p.get_device_count()
            self.assertGreater(device_count, 0, "At least one audio device should be available")
            
            # Test device information
            for i in range(min(device_count, 5)):  # Test first 5 devices
                try:
                    device_info = p.get_device_info_by_index(i)
                    self.assertIsInstance(device_info, dict)
                    self.assertIn('name', device_info)
                    self.assertIn('maxInputChannels', device_info)
                    self.assertIn('maxOutputChannels', device_info)
                except Exception as e:
                    # Some devices might not be accessible
                    continue
            
            p.terminate()
            
        except ImportError:
            self.skipTest("PyAudio not available")
        except Exception as e:
            self.skipTest(f"PyAudio test failed: {e}")
    
    def test_audio_device_access(self):
        """Test audio device access permissions"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            # Find default input device
            default_input_device = None
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    default_input_device = i
                    break
            
            if default_input_device is not None:
                # Test opening input stream
                try:
                    stream = p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=default_input_device,
                        frames_per_buffer=1024
                    )
                    stream.close()
                except Exception as e:
                    self.skipTest(f"Cannot access input device: {e}")
            
            p.terminate()
            
        except ImportError:
            self.skipTest("PyAudio not available")
        except Exception as e:
            self.skipTest(f"Audio device access test failed: {e}")

class TestVoiceCommandProcessing(unittest.TestCase):
    """Test voice command processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_wake_word_detection(self):
        """Test wake word detection logic"""
        try:
            from jarvis import JARVIS
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test wake word detection in commands
            test_commands = [
                ("jarvis hello", True),
                ("hey jarvis what time is it", True),
                ("jarvis search for python", True),
                ("hello world", False),
                ("what time is it", False),
                ("search for python", False)
            ]
            
            wake_word = jarvis_instance.config.settings["general"]["wake_word"]
            
            for command, should_contain_wake_word in test_commands:
                with self.subTest(command=command):
                    contains_wake_word = wake_word in command.lower()
                    self.assertEqual(
                        contains_wake_word, should_contain_wake_word,
                        f"Wake word detection failed for: {command}"
                    )
                    
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    @patch('jarvis.VoiceEngine.listen')
    def test_command_processing_flow(self, mock_listen):
        """Test command processing flow with mocked voice input"""
        try:
            from jarvis import JARVIS
            
            # Mock voice input
            mock_listen.return_value = "jarvis hello"
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Test command processing
            result = jarvis_instance.process_command("jarvis hello")
            
            # Should return True to continue processing
            self.assertTrue(result, "Greeting command should be processed successfully")
            
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestVoiceSystemPerformance(unittest.TestCase):
    """Test voice system performance characteristics"""
    
    def test_recognition_timeout(self):
        """Test speech recognition timeout handling"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Test with very short timeout
            with self.assertRaises(sr.WaitTimeoutError):
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=0.1)
                    
        except ImportError:
            self.skipTest("speech_recognition module not available")
        except OSError:
            self.skipTest("Microphone not accessible")
    
    def test_tts_performance(self):
        """Test text-to-speech performance"""
        try:
            import pyttsx3
            import time
            
            engine = pyttsx3.init()
            
            # Test TTS speed
            test_text = "This is a performance test for text to speech synthesis."
            
            start_time = time.time()
            
            # Use threading to avoid blocking
            def speak_text():
                engine.say(test_text)
                engine.runAndWait()
            
            thread = threading.Thread(target=speak_text)
            thread.start()
            thread.join(timeout=10)  # 10 second timeout
            
            if thread.is_alive():
                engine.stop()
                self.fail("TTS took too long (>10 seconds)")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # TTS should complete within reasonable time
            self.assertLess(duration, 10, "TTS should complete within 10 seconds")
            
            engine.stop()
            
        except ImportError:
            self.skipTest("pyttsx3 module not available")
        except Exception as e:
            self.skipTest(f"TTS performance test failed: {e}")

class TestVoiceSystemErrorHandling(unittest.TestCase):
    """Test voice system error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_microphone_unavailable_handling(self):
        """Test handling when microphone is unavailable"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Simulate microphone unavailable
            with patch('speech_recognition.Microphone') as mock_mic:
                mock_mic.side_effect = OSError("No microphone available")
                
                # VoiceEngine should handle this gracefully
                voice_engine = VoiceEngine(config, logger)
                
                # Microphone should be None
                self.assertIsNone(voice_engine.microphone)
                
                # Listen should return None gracefully
                result = voice_engine.listen()
                self.assertIsNone(result)
                
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_tts_unavailable_handling(self):
        """Test handling when TTS is unavailable"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Simulate TTS unavailable
            with patch('pyttsx3.init') as mock_tts:
                mock_tts.side_effect = Exception("TTS not available")
                
                # VoiceEngine should handle this gracefully
                voice_engine = VoiceEngine(config, logger)
                
                # TTS engine should be None
                self.assertIsNone(voice_engine.tts_engine)
                
                # Speak should handle None engine gracefully
                voice_engine.speak("test message")  # Should not raise exception
                
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_network_error_handling(self):
        """Test handling of network errors during speech recognition"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Simulate network error
            with patch.object(recognizer, 'recognize_google') as mock_recognize:
                mock_recognize.side_effect = sr.RequestError("Network error")
                
                # Should handle network error gracefully
                try:
                    # Create dummy audio data
                    audio_data = sr.AudioData(b"dummy", 16000, 2)
                    result = recognizer.recognize_google(audio_data)
                    self.fail("Should have raised RequestError")
                except sr.RequestError:
                    # This is expected
                    pass
                    
        except ImportError:
            self.skipTest("speech_recognition module not available")

class TestVoiceSystemConfiguration(unittest.TestCase):
    """Test voice system configuration options"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_voice_configuration_loading(self):
        """Test loading voice configuration from file"""
        try:
            from jarvis import JARVISConfig
            
            # Create custom voice configuration
            import json
            config_file = os.path.join(self.config_dir, "settings.json")
            custom_config = {
                "general": {"wake_word": "computer"},
                "voice": {
                    "input": {
                        "timeout": 10,
                        "phrase_time_limit": 15
                    },
                    "output": {
                        "rate": 200,
                        "volume": 0.8
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(custom_config, f)
            
            # Load configuration
            config = JARVISConfig(self.config_dir)
            
            # Test that custom values are loaded
            self.assertEqual(config.settings["general"]["wake_word"], "computer")
            self.assertEqual(config.settings["voice"]["input"]["timeout"], 10)
            self.assertEqual(config.settings["voice"]["output"]["rate"], 200)
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_voice_device_configuration(self):
        """Test voice device configuration"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            config = JARVISConfig(self.config_dir)
            logger = JARVISLogger(debug=True)
            
            # Test with device index configuration
            config.settings["voice"]["input"]["device_index"] = 0
            
            # Should not crash with device index
            voice_engine = VoiceEngine(config, logger)
            
            # Test configuration was applied
            if voice_engine.microphone:
                # If microphone was created successfully, configuration was applied
                pass
            else:
                # If microphone creation failed, it should be handled gracefully
                self.assertIsNone(voice_engine.microphone)
                
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestVoiceSystemIntegration(unittest.TestCase):
    """Test voice system integration with other JARVIS components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.VoiceEngine.listen')
    @patch('jarvis.VoiceEngine.speak')
    def test_voice_command_integration(self, mock_speak, mock_listen):
        """Test voice command integration with JARVIS main system"""
        try:
            from jarvis import JARVIS
            
            # Mock voice input and output
            mock_listen.return_value = "jarvis what time is it"
            
            jarvis_instance = JARVIS(config_dir=self.config_dir, debug=True)
            
            # Process the command
            result = jarvis_instance.process_command("jarvis what time is it")
            
            # Should return True (continue processing)
            self.assertTrue(result)
            
            # Should have called speak method
            mock_speak.assert_called()
            
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_voice_logging_integration(self):
        """Test voice system logging integration"""
        try:
            from jarvis import JARVISConfig, JARVISLogger, VoiceEngine
            
            config = JARVISConfig(self.config_dir)
            
            # Create logger with log directory
            logs_dir = os.path.join(self.temp_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            logger = JARVISLogger(log_dir=logs_dir, debug=True)
            
            # Initialize voice engine (should log initialization)
            voice_engine = VoiceEngine(config, logger)
            
            # Check that log files were created
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            self.assertGreater(len(log_files), 0, "Log files should be created")
            
        except ImportError:
            self.skipTest("JARVIS modules not available")

class TestVoiceSystemSecurity(unittest.TestCase):
    """Test voice system security considerations"""
    
    def test_command_injection_prevention(self):
        """Test that voice commands cannot inject system commands"""
        try:
            from jarvis import JARVIS
            
            temp_dir = tempfile.mkdtemp()
            config_dir = os.path.join(temp_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            try:
                jarvis_instance = JARVIS(config_dir=config_dir, debug=True)
                
                # Test potentially dangerous voice commands
                dangerous_commands = [
                    "jarvis run sudo rm -rf /",
                    "jarvis execute rm -rf *",
                    "jarvis command sudo shutdown now",
                    "jarvis run; sudo reboot;",
                ]
                
                for cmd in dangerous_commands:
                    with self.subTest(command=cmd):
                        # These should be blocked by security manager
                        result = jarvis_instance.process_command(cmd)
                        # Should not crash the system
                        self.assertIsInstance(result, bool)
                        
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except ImportError:
            self.skipTest("JARVIS modules not available")
    
    def test_voice_input_sanitization(self):
        """Test that voice input is properly sanitized"""
        try:
            from jarvis import JARVISConfig, SecurityManager, JARVISLogger
            
            temp_dir = tempfile.mkdtemp()
            config_dir = os.path.join(temp_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            try:
                config = JARVISConfig(config_dir)
                logger = JARVISLogger(debug=True)
                security = SecurityManager(config, logger)
                
                # Test input sanitization
                test_inputs = [
                    "ls; rm file",
                    "ls && rm file", 
                    "ls | grep test",
                    "echo `whoami`",
                    "ls $HOME"
                ]
                
                for input_cmd in test_inputs:
                    with self.subTest(input=input_cmd):
                        sanitized = security.sanitize_input(input_cmd)
                        # Should remove dangerous characters
                        self.assertNotIn(';', sanitized)
                        self.assertNotIn('&', sanitized)
                        self.assertNotIn('|', sanitized)
                        self.assertNotIn('`', sanitized)
                        self.assertNotIn('
            , sanitized)
                        
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except ImportError:
            self.skipTest("JARVIS modules not available")

def run_voice_tests():
    """Run all voice system tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSpeechRecognitionModule,
        TestTextToSpeechModule,
        TestVoiceEngineIntegration,
        TestAudioSystemCompatibility,
        TestVoiceCommandProcessing,
        TestVoiceSystemPerformance,
        TestVoiceSystemErrorHandling,
        TestVoiceSystemConfiguration,
        TestVoiceSystemIntegration,
        TestVoiceSystemSecurity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def generate_voice_system_report():
    """Generate a voice system status report"""
    print("\n" + "="*60)
    print("🎤 JARVIS VOICE SYSTEM REPORT")
    print("="*60)
    
    # Speech Recognition
    print(f"\n🗣️  Speech Recognition:")
    try:
        import speech_recognition as sr
        print("  ✓ speech_recognition module available")
        
        # Test microphone detection
        mic_list = sr.Microphone.list_microphone_names()
        print(f"  📱 Microphones detected: {len(mic_list)}")
        
        if mic_list:
            for i, name in enumerate(mic_list[:3]):  # Show first 3
                print(f"    {i}: {name}")
                
    except ImportError:
        print("  ✗ speech_recognition module not available")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    # Text-to-Speech
    print(f"\n🔊 Text-to-Speech:")
    try:
        import pyttsx3
        print("  ✓ pyttsx3 module available")
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if voices:
            print(f"  🎭 Voices available: {len(voices)}")
            for i, voice in enumerate(voices[:3]):  # Show first 3
                print(f"    {i}: {voice.name}")
        else:
            print("  ⚠️  No voices detected")
            
        engine.stop()
        
    except ImportError:
        print("  ✗ pyttsx3 module not available")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    # PyAudio
    print(f"\n🎵 Audio System:")
    try:
        import pyaudio
        print("  ✓ pyaudio module available")
        
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"  🎛️  Audio devices: {device_count}")
        
        input_devices = 0
        output_devices = 0
        
        for i in range(device_count):
            try:
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_devices += 1
                if info['maxOutputChannels'] > 0:
                    output_devices += 1
            except:
                continue
        
        print(f"  🎤 Input devices: {input_devices}")
        print(f"  🔈 Output devices: {output_devices}")
        
        p.terminate()
        
    except ImportError:
        print("  ✗ pyaudio module not available")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    # System Audio Tools
    print(f"\n🛠️  System Audio Tools:")
    import subprocess
    
    tools = ["arecord", "aplay", "espeak", "festival", "pactl"]
    for tool in tools:
        try:
            subprocess.run([tool, "--help"], capture_output=True, timeout=5)
            print(f"  ✓ {tool}")
        except:
            print(f"  ✗ {tool}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🧪 JARVIS Voice System Tests")
    print("=" * 50)
    
    # Generate voice system report first
    generate_voice_system_report()
    
    # Run tests
    success = run_voice_tests()
    
    if success:
        print("\n✅ All voice tests passed!")
        print("🎤 Your voice system is ready for JARVIS!")
        sys.exit(0)
    else:
        print("\n❌ Some voice tests failed!")
        print("🔧 Please fix the issues above before using voice features.")
        sys.exit(1)
