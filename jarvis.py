#!/usr/bin/env python3
"""
JARVIS Voice Assistant - Main Application
Author: Fahad Al Maashani
Version: 1.0.0
Description: A sophisticated voice-controlled AI assistant inspired by Iron Man's JARVIS
"""

import os
import sys
import json
import time
import threading
import subprocess
import signal
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import queue

# Third-party imports
try:
    import speech_recognition as sr
    import pyttsx3
    import requests
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.align import Align
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from googlesearch import search
    import wikipedia
    import psutil
    from rich.columns import Columns
    from rich.rule import Rule
except ImportError as e:
    print(f"Error: Missing required module: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

class JARVISConfig:
    """Configuration manager for JARVIS"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings = self.load_settings()
        self.audio_config = self.load_audio_config()
        self.security_config = self.load_security_config()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load main settings configuration"""
        settings_file = self.config_dir / "settings.json"
        default_settings = {
            "general": {
                "wake_word": "jarvis",
                "name": "JARVIS",
                "version": "1.0.0",
                "debug": False
            },
            "voice": {
                "input": {
                    "timeout": 5,
                    "phrase_time_limit": 10,
                    "ambient_duration": 1,
                    "device_index": None
                },
                "output": {
                    "rate": 180,
                    "volume": 0.9,
                    "voice_id": None
                }
            },
            "ui": {
                "theme": "matrix",
                "colors": {
                    "primary": "green",
                    "secondary": "cyan",
                    "accent": "blue",
                    "text": "white"
                },
                "animations": True
            },
            "features": {
                "web_search": True,
                "wikipedia": True,
                "weather": False,
                "email": False
            }
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                self.config_dir.mkdir(exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return default_settings
    
    def load_audio_config(self) -> Dict[str, Any]:
        """Load audio configuration"""
        return {
            "input": {
                "device_name": None,
                "sample_rate": 16000,
                "chunk_size": 1024,
                "channels": 1
            },
            "output": {
                "device_name": None,
                "volume": 0.8
            }
        }
    
    def load_security_config(self) -> Dict[str, Any]:
        """Load security configuration"""
        return {
            "allowed_commands": [
                "ls", "pwd", "cat", "head", "tail", "grep", "find", "wc",
                "ps", "top", "df", "free", "uptime", "uname", "whoami",
                "ping", "curl", "wget", "traceroute",
                "git", "python3", "pip3", "node", "npm"
            ],
            "forbidden_patterns": [
                "sudo", "su", "chmod 777", "rm -rf", "mkfs", "fdisk",
                "passwd", "useradd", "userdel", "systemctl", "service"
            ],
            "max_execution_time": 30,
            "max_output_size": 10000
        }

class JARVISLogger:
    """Advanced logging system for JARVIS"""
    
    def __init__(self, log_dir: str = "logs", debug: bool = False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        
        # Main logger
        self.logger = logging.getLogger('JARVIS')
        self.logger.setLevel(log_level)
        
        # File handler
        log_file = self.log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class VoiceEngine:
    """Voice recognition and synthesis engine"""
    
    def __init__(self, config: JARVISConfig, logger: JARVISLogger):
        self.config = config
        self.logger = logger
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.setup_voice_recognition()
        self.setup_text_to_speech()
    
    def setup_voice_recognition(self):
        """Initialize speech recognition"""
        try:
            # Get microphone device
            device_index = self.config.settings["voice"]["input"]["device_index"]
            self.microphone = sr.Microphone(device_index=device_index)
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=self.config.settings["voice"]["input"]["ambient_duration"]
                )
            
            self.logger.info("Voice recognition initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Voice recognition setup failed: {e}")
            self.microphone = None
    
    def setup_text_to_speech(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.tts_engine.getProperty('voices')
            voice_id = self.config.settings["voice"]["output"]["voice_id"]
            
            if voice_id and voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
            else:
                # Try to find a male voice
                for voice in voices:
                    if voice and ('male' in voice.name.lower() or 'david' in voice.name.lower()):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.setProperty('rate', self.config.settings["voice"]["output"]["rate"])
            self.tts_engine.setProperty('volume', self.config.settings["voice"]["output"]["volume"])
            
            self.logger.info("Text-to-speech initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Text-to-speech setup failed: {e}")
            self.tts_engine = None
    
    def listen(self) -> Optional[str]:
        """Listen for voice commands"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.settings["voice"]["input"]["timeout"],
                    phrase_time_limit=self.config.settings["voice"]["input"]["phrase_time_limit"]
                )
            
            # Recognize speech using Google
            command = self.recognizer.recognize_google(audio).lower()
            self.logger.info(f"Voice command recognized: {command}")
            return command
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Voice recognition error: {e}")
            return None
    
    def speak(self, text: str, priority: bool = False):
        """Convert text to speech"""
        if not self.tts_engine:
            return
        
        try:
            # Limit text length for speech
            if len(text) > 200 and not priority:
                text = text[:200] + "... Check screen for full details."
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            self.logger.debug(f"Spoke: {text[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {e}")

class SecurityManager:
    """Security manager for safe command execution"""
    
    def __init__(self, config: JARVISConfig, logger: JARVISLogger):
        self.config = config
        self.logger = logger
        self.allowed_commands = set(config.security_config["allowed_commands"])
        self.forbidden_patterns = config.security_config["forbidden_patterns"]
    
    def validate_command(self, command: str) -> bool:
        """Validate if command is safe to execute"""
        command = command.strip().lower()
        
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern in command:
                self.logger.warning(f"Forbidden pattern detected: {pattern}")
                return False
        
        # Check if base command is allowed
        base_command = command.split()[0] if command.split() else ""
        if base_command not in self.allowed_commands:
            self.logger.warning(f"Command not whitelisted: {base_command}")
            return False
        
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input"""
        # Remove dangerous characters
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>']
        for char in dangerous_chars:
            user_input = user_input.replace(char, '')
        
        return user_input.strip()

class CommandProcessor:
    """Process and execute system commands safely"""
    
    def __init__(self, config: JARVISConfig, logger: JARVISLogger, security: SecurityManager):
        self.config = config
        self.logger = logger
        self.security = security
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute system command safely"""
        # Sanitize input
        command = self.security.sanitize_input(command)
        
        # Validate command
        if not self.security.validate_command(command):
            return {
                "status": "error",
                "message": "Command not allowed for security reasons",
                "output": ""
            }
        
        try:
            # Execute with timeout
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=self.config.security_config["max_execution_time"],
                cwd=os.path.expanduser("~")
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            # Limit output size
            max_size = self.config.security_config["max_output_size"]
            if len(output) > max_size:
                output = output[:max_size] + "\n... (output truncated)"
            
            self.logger.info(f"Command executed: {command}")
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output,
                "error": error,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Command timeout: {command}")
            return {
                "status": "error",
                "message": "Command timed out",
                "output": ""
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "message": "Command not found",
                "output": ""
            }
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "output": ""
            }

class WebInterface:
    """Web search and online services interface"""
    
    def __init__(self, config: JARVISConfig, logger: JARVISLogger):
        self.config = config
        self.logger = logger
    
    def search_web(self, query: str, num_results: int = 5) -> List[str]:
        """Search the web using Google"""
        try:
            self.logger.info(f"Web search: {query}")
            results = []
            
            search_results = list(search(query, num_results=num_results, stop=num_results, pause=1))
            
            for i, url in enumerate(search_results, 1):
                results.append(f"{i}. {url}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
            return [f"Search failed: {str(e)}"]
    
    def get_wikipedia_summary(self, topic: str) -> str:
        """Get Wikipedia summary"""
        try:
            self.logger.info(f"Wikipedia search: {topic}")
            
            # Get summary
            summary = wikipedia.summary(topic, sentences=3, auto_suggest=True)
            
            # Get page URL
            page = wikipedia.page(topic, auto_suggest=True)
            
            return f"{summary}\n\nSource: {page.url}"
            
        except wikipedia.exceptions.DisambiguationError as e:
            options = ", ".join(e.options[:5])
            return f"Multiple topics found. Try: {options}"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{topic}'"
        except Exception as e:
            self.logger.error(f"Wikipedia error: {e}")
            return f"Wikipedia lookup failed: {str(e)}"
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        try:
            info = {}
            
            # CPU info
            info["CPU Usage"] = f"{psutil.cpu_percent(interval=1):.1f}%"
            
            # Memory info
            memory = psutil.virtual_memory()
            info["Memory Usage"] = f"{memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)"
            
            # Disk info
            disk = psutil.disk_usage('/')
            info["Disk Usage"] = f"{disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)"
            
            # Network info
            net_io = psutil.net_io_counters()
            info["Network"] = f"↑{net_io.bytes_sent // (1024**2):.1f}MB ↓{net_io.bytes_recv // (1024**2):.1f}MB"
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            info["Uptime"] = f"{hours}h {minutes}m"
            
            return info
            
        except Exception as e:
            self.logger.error(f"System info error: {e}")
            return {"Error": str(e)}

class UIManager:
    """User interface manager with rich terminal display"""
    
    def __init__(self, config: JARVISConfig, logger: JARVISLogger):
        self.config = config
        self.logger = logger
        self.console = Console()
        self.colors = config.settings["ui"]["colors"]
        self.theme = config.settings["ui"]["theme"]
    
    def create_header(self) -> Panel:
        """Create JARVIS header"""
        ascii_art = Text.assemble(
            ("     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗\n", self.colors["primary"]),
            ("     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝\n", self.colors["primary"]),
            ("     ██║███████║██████╔╝██║   ██║██║███████╗\n", self.colors["primary"]),
            ("██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║\n", self.colors["primary"]),
            ("╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║\n", self.colors["primary"]),
            (" ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝\n", self.colors["primary"]),
            ("        Personal AI Assistant v1.0.0", self.colors["secondary"])
        )
        
        return Panel(
            Align.center(ascii_art),
            style=self.colors["primary"],
            border_style=self.colors["accent"]
        )
    
    def create_status_panel(self, status: str = "LISTENING") -> Panel:
        """Create status panel"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        status_text = Text.assemble(
            ("🎤 Status: ", "white"),
            (status, self.colors["primary"]),
            (" | ", "white"),
            ("⏰ Time: ", "white"),
            (current_time, self.colors["secondary"]),
            (" | ", "white"),
            ("🔊 Ready for voice commands", self.colors["accent"])
        )
        
        return Panel(
            Align.center(status_text),
            title="System Status",
            style=self.colors["secondary"]
        )
    
    def create_main_layout(self, status: str = "LISTENING") -> Layout:
        """Create main UI layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=8),
            Layout(name="main"),
            Layout(name="footer", size=4)
        )
        
        layout["header"].update(self.create_header())
        layout["footer"].update(self.create_status_panel(status))
        
        # Main content
        instructions = Text.assemble(
            ("🎙️ Say 'JARVIS' followed by your command\n\n", "white"),
            ("Examples:\n", self.colors["accent"]),
            ("• 'Jarvis, hello' - Greeting\n", self.colors["secondary"]),
            ("• 'Jarvis, what time is it?' - Current time\n", self.colors["secondary"]),
            ("• 'Jarvis, search for Python tutorials' - Web search\n", self.colors["secondary"]),
            ("• 'Jarvis, system status' - System information\n", self.colors["secondary"]),
            ("• 'Jarvis, goodbye' - Exit\n", self.colors["secondary"])
        )
        
        layout["main"].update(Panel(
            Align.center(instructions),
            title="Voice Commands",
            style=self.colors["primary"]
        ))
        
        return layout
    
    def display_response(self, response: str, response_type: str = "info"):
        """Display JARVIS response"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "info": self.colors["secondary"],
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        
        color = color_map.get(response_type, self.colors["secondary"])
        
        response_panel = Panel(
            Text(response, style=color),
            title=f"JARVIS Response - {timestamp}",
            border_style=color
        )
        
        self.console.print(response_panel)
    
    def display_command_output(self, output: str, command: str):
        """Display command output"""
        if not output:
            return
        
        output_panel = Panel(
            Text(output, style="white"),
            title=f"Command Output: {command}",
            border_style=self.colors["accent"]
        )
        
        self.console.print(output_panel)
    
    def display_system_info(self, info: Dict[str, str]):
        """Display system information table"""
        table = Table(title="System Information")
        table.add_column("Property", style=self.colors["secondary"])
        table.add_column("Value", style=self.colors["primary"])
        
        for prop, value in info.items():
            table.add_row(prop, value)
        
        self.console.print(table)
    
    def clear_screen(self):
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

class JARVIS:
    """Main JARVIS Voice Assistant class"""
    
    def __init__(self, config_dir: str = "config", debug: bool = False):
        # Initialize components
        self.config = JARVISConfig(config_dir)
        self.logger = JARVISLogger(debug=debug)
        self.security = SecurityManager(self.config, self.logger)
        self.voice = VoiceEngine(self.config, self.logger)
        self.commands = CommandProcessor(self.config, self.logger, self.security)
        self.web = WebInterface(self.config, self.logger)
        self.ui = UIManager(self.config, self.logger)
        
        # State management
        self.running = False
        self.last_activity = time.time()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("JARVIS initialized successfully")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        self.shutdown()
    
    def startup_sequence(self):
        """JARVIS startup sequence"""
        self.ui.clear_screen()
        
        startup_messages = [
            "Initializing JARVIS systems...",
            "Loading voice recognition engine...",
            "Configuring text-to-speech synthesis...",
            "Establishing web connectivity...",
            "Loading security protocols...",
            "All systems operational.",
            "JARVIS is ready for your commands, sir."
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.ui.console
        ) as progress:
            
            for message in startup_messages:
                task = progress.add_task(message, total=None)
                time.sleep(0.8)
                progress.remove_task(task)
        
        # Welcome message
        welcome_msg = "Good day, sir. JARVIS at your service. All systems operational and ready for your commands."
        self.voice.speak(welcome_msg, priority=True)
        self.logger.info("JARVIS startup completed")
    
    def process_command(self, command: str) -> bool:
        """Process voice command and return whether to continue"""
        if not command:
            return True
        
        # Update activity timestamp
        self.last_activity = time.time()
        
        # Remove wake word
        wake_word = self.config.settings["general"]["wake_word"]
        if wake_word in command:
            command = command.replace(wake_word, "").strip()
        else:
            # No wake word detected
            return True
        
        self.logger.info(f"Processing command: {command}")
        
        # Exit commands
        if any(word in command for word in ["goodbye", "exit", "quit", "shutdown", "power down"]):
            return self.handle_goodbye()
        
        # Greeting commands
        elif any(word in command for word in ["hello", "hi", "good morning", "good evening", "how are you"]):
            return self.handle_greeting()
        
        # Time and date
        elif "time" in command:
            return self.handle_time()
        elif "date" in command:
            return self.handle_date()
        
        # System information
        elif any(phrase in command for phrase in ["system status", "system info", "show stats"]):
            return self.handle_system_info()
        
        # System commands
        elif any(command.startswith(prefix) for prefix in ["run ", "execute ", "command "]):
            return self.handle_system_command(command)
        
        # Web search
        elif any(command.startswith(prefix) for prefix in ["search ", "google ", "look up "]):
            return self.handle_web_search(command)
        
        # Wikipedia
        elif any(command.startswith(prefix) for prefix in ["wiki ", "wikipedia "]) or "tell me about" in command:
            return self.handle_wikipedia(command)
        
        # Help
        elif any(word in command for word in ["help", "what can you do", "commands"]):
            return self.handle_help()
        
        # Default response
        else:
            return self.handle_unknown_command()
    
    def handle_goodbye(self) -> bool:
        """Handle goodbye command"""
        goodbye_msg = "Shutting down all systems. It has been a pleasure serving you today, sir. Goodbye."
        self.voice.speak(goodbye_msg, priority=True)
        self.ui.display_response(goodbye_msg, "info")
        return False
    
    def handle_greeting(self) -> bool:
        """Handle greeting commands"""
        greetings = [
            "Hello, sir. How may I assist you today?",
            "Good to see you again, sir. All systems are at your disposal.",
            "Greetings. JARVIS reporting for duty.",
            "Hello, sir. What can I do for you today?"
        ]
        
        import random
        response = random.choice(greetings)
        self.voice.speak(response)
        self.ui.display_response(response, "success")
        return True
    
    def handle_time(self) -> bool:
        """Handle time request"""
        current_time = datetime.now().strftime("%I:%M %p")
        response = f"The current time is {current_time}."
        self.voice.speak(response)
        self.ui.display_response(response, "info")
        return True
    
    def handle_date(self) -> bool:
        """Handle date request"""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        response = f"Today is {current_date}."
        self.voice.speak(response)
        self.ui.display_response(response, "info")
        return True
    
    def handle_system_info(self) -> bool:
        """Handle system information request"""
        info = self.web.get_system_info()
        self.ui.display_system_info(info)
        self.voice.speak("System information displayed on screen.")
        return True
    
    def handle_system_command(self, command: str) -> bool:
        """Handle system command execution"""
        # Extract actual command
        for prefix in ["run ", "execute ", "command "]:
            if command.startswith(prefix):
                actual_command = command[len(prefix):].strip()
                break
        else:
            actual_command = command
        
        result = self.commands.execute_command(actual_command)
        
        if result["status"] == "success":
            self.voice.speak("Command executed successfully.")
            self.ui.display_command_output(result["output"], actual_command)
        else:
            error_msg = result.get("message", "Command execution failed")
            self.voice.speak(f"Command failed: {error_msg}")
            self.ui.display_response(error_msg, "error")
        
        return True
    
    def handle_web_search(self, command: str) -> bool:
        """Handle web search request"""
        # Extract search query
        for prefix in ["search ", "google ", "look up "]:
            if command.startswith(prefix):
                query = command[len(prefix):].strip()
                break
        else:
            query = command
        
        if not query:
            self.voice.speak("What would you like me to search for?")
            return True
        
        results = self.web.search_web(query)
        
        if results:
            self.voice.speak(f"I found {len(results)} search results for {query}. Check the screen for details.")
            result_text = "\n".join(results)
            self.ui.display_response(f"Search results for '{query}':\n\n{result_text}", "info")
        else:
            self.voice.speak("No search results found.")
            self.ui.display_response("No search results found.", "warning")
        
        return True
    
    def handle_wikipedia(self, command: str) -> bool:
        """Handle Wikipedia lookup"""
        # Extract topic
        for prefix in ["wiki ", "wikipedia ", "tell me about "]:
            if command.startswith(prefix):
                topic = command[len(prefix):].strip()
                break
        else:
            topic = command
        
        if not topic:
            self.voice.speak("What topic would you like me to look up?")
            return True
        
        summary = self.web.get_wikipedia_summary(topic)
        
        # Speak a brief version
        brief_summary = summary.split('\n')[0]  # First line only for speech
        self.voice.speak(f"Here's what I found about {topic}: {brief_summary[:150]}...")
        self.ui.display_response(f"Wikipedia summary for '{topic}':\n\n{summary}", "info")
        
        return True
    
    def handle_help(self) -> bool:
        """Handle help request"""
        help_text = """
Available Commands:
• Greetings: "Jarvis, hello" or "Jarvis, good morning"
• Time & Date: "Jarvis, what time is it?" or "Jarvis, what's the date?"
• System Info: "Jarvis, system status" or "Jarvis, show stats"
• System Commands: "Jarvis, run ls" or "Jarvis, execute ps"
• Web Search: "Jarvis, search for Python tutorials"
• Wikipedia: "Jarvis, wiki Albert Einstein" or "Jarvis, tell me about quantum physics"
• Exit: "Jarvis, goodbye" or "Jarvis, shutdown"

Just say 'Jarvis' followed by your command!
        """
        
        self.voice.speak("I can help with system commands, web searches, Wikipedia lookups, and general assistance. Check the screen for a complete list.")
        self.ui.display_response(help_text.strip(), "info")
        return True
    
    def handle_unknown_command(self) -> bool:
        """Handle unknown commands"""
        responses = [
            "I'm not sure how to help with that request, sir. Try saying 'Jarvis help' for available commands.",
            "I don't understand that command. Say 'Jarvis help' to see what I can do.",
            "That command is not recognized. Please try rephrasing or ask for help.",
            "I'm afraid I don't have that capability yet. Say 'Jarvis help' for available commands."
        ]
        
        import random
        response = random.choice(responses)
        self.voice.speak(response)
        self.ui.display_response(response, "warning")
        return True
    
    def run(self):
        """Main JARVIS execution loop"""
        try:
            # Startup sequence
            self.startup_sequence()
            self.running = True
            
            # Main interaction loop
            while self.running:
                try:
                    # Create and display main UI
                    with Live(self.ui.create_main_layout(), refresh_per_second=1, screen=False) as live:
                        # Listen for voice commands
                        command = self.voice.listen()
                        
                        if command:
                            # Display user input
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            self.ui.console.print(f"[green]{timestamp} You:[/green] {command}")
                            
                            # Process command
                            should_continue = self.process_command(command)
                            if not should_continue:
                                break
                            
                            # Brief pause between commands
                            time.sleep(0.5)
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Runtime error: {e}")
                    self.ui.display_response(f"System error: {e}", "error")
                    time.sleep(1)
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.ui.display_response(f"Fatal error: {e}", "error")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        self.logger.info("JARVIS shutting down")
        
        # Cleanup voice engine
        if self.voice.tts_engine:
            try:
                self.voice.tts_engine.stop()
            except:
                pass
        
        self.ui.console.print("[yellow]JARVIS systems offline. Thank you for using JARVIS![/yellow]")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="JARVIS Voice Assistant")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", default="config", help="Configuration directory")
    parser.add_argument("--version", action="version", version="JARVIS 1.0.0")
    
    args = parser.parse_args()
    
    try:
        # Create JARVIS instance
        jarvis = JARVIS(config_dir=args.config, debug=args.debug)
        
        # Run JARVIS
        jarvis.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Failed to start JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
