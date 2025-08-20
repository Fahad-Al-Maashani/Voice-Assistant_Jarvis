#!/bin/bash

# JARVIS Voice Assistant - Professional Setup Script
# Author: Fahad Al Maashani
# Description: Automated installation and configuration for JARVIS

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Project information
PROJECT_NAME="JARVIS Voice Assistant"
PROJECT_VERSION="1.0.0"
AUTHOR="Fahad Al Maashani"
REPO_URL="https://github.com/Fahad-Al-Maashani/Voice-Assistant_Jarvis"

# Installation directories
INSTALL_DIR="$HOME/jarvis-assistant"
VENV_DIR="$INSTALL_DIR/venv"
CONFIG_DIR="$INSTALL_DIR/config"
LOGS_DIR="$INSTALL_DIR/logs"

# Print banner
print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          🤖 JARVIS Voice Assistant                          ║"
    echo "║                              Setup & Installation                           ║"
    echo "║                                                                              ║"
    echo "║                         Author: Fahad Al Maashani                           ║"
    echo "║                              Version: v1.0.0                                ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
# Logging function
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

# Warning function
warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Error function
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if running on supported system
check_system() {
    log "Checking system compatibility..."
    
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        error "This installer is designed for Linux systems only."
    fi
    
    # Check for Ubuntu/Debian
    if ! command -v apt &> /dev/null; then
        warn "This script is optimized for Ubuntu/Debian. Continuing anyway..."
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" ]] && [[ "$ARCH" != "aarch64" ]]; then
        warn "Architecture $ARCH may not be fully supported."
    fi
    
    log "System check completed ✓"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 ]] && [[ $PYTHON_MINOR -ge 8 ]]; then
            log "Python $PYTHON_VERSION found ✓"
        else
            error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        fi
    else
        error "Python 3 is not installed. Please install Python 3.8 or higher."
    fi
    
    # Check internet connectivity
    if ping -c 1 google.com &> /dev/null; then
        log "Internet connectivity verified ✓"
    else
        error "Internet connection required for installation."
    fi
    
    # Check available disk space (minimum 2GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [[ $AVAILABLE_SPACE -lt 2097152 ]]; then  # 2GB in KB
        error "Insufficient disk space. At least 2GB required."
    fi
    
    log "Prerequisites check completed ✓"
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    # Update package list
    sudo apt update -qq
    
    # Essential packages
    local packages=(
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "build-essential"
        "portaudio19-dev"
        "libasound2-dev"
        "libportaudio2"
        "libportaudiocpp0"
        "ffmpeg"
        "espeak"
        "espeak-data"
        "alsa-utils"
        "pulseaudio"
        "pulseaudio-utils"
        "git"
        "curl"
        "wget"
        "unzip"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
    )
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log "✓ $package already installed"
        else
            log "Installing $package..."
            sudo apt install -y "$package" || warn "Failed to install $package"
        fi
    done
    
    log "System dependencies installation completed ✓"
}

# Setup audio system
setup_audio() {
    log "Configuring audio system..."
    
    # Add user to audio group
    sudo usermod -a -G audio $USER
    
    # Start PulseAudio if not running
    if ! pgrep -x "pulseaudio" > /dev/null; then
        log "Starting PulseAudio..."
        pulseaudio --start --log-target=syslog
    fi
    
    # Test audio devices
    if arecord -l | grep -q "card"; then
        log "Audio input devices detected ✓"
    else
        warn "No audio input devices found. Please check your microphone."
    fi
    
    if aplay -l | grep -q "card"; then
        log "Audio output devices detected ✓"
    else
        warn "No audio output devices found. Please check your speakers."
    fi
    
    log "Audio system configuration completed ✓"
}

# Create project structure
create_structure() {
    log "Creating project structure..."
    
    # Create main directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$INSTALL_DIR/scripts"
    mkdir -p "$INSTALL_DIR/modules"
    mkdir -p "$INSTALL_DIR/assets"
    mkdir -p "$INSTALL_DIR/docs"
    mkdir -p "$INSTALL_DIR/tests"
    
    log "Project structure created ✓"
}

# Setup Python virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log "Virtual environment created ✓"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install core dependencies first
    local core_deps=(
        "wheel"
        "setuptools"
        "cython"
        "numpy"
    )
    
    for dep in "${core_deps[@]}"; do
        log "Installing $dep..."
        pip install "$dep" --no-cache-dir
    done
    
    # Install main dependencies
    if [[ -f "requirements.txt" ]]; then
        log "Installing from requirements.txt..."
        pip install -r requirements.txt --no-cache-dir
    else
        # Fallback to essential packages
        local essential_deps=(
            "SpeechRecognition==3.10.0"
            "pyttsx3==2.90"
            "pyaudio==0.2.11"
            "rich==13.7.1"
            "requests==2.31.0"
            "googlesearch-python==1.2.3"
            "wikipedia==1.4.0"
            "psutil==5.9.6"
            "colorama==0.4.6"
            "python-dateutil==2.8.2"
        )
        
        for dep in "${essential_deps[@]}"; do
            log "Installing $dep..."
            pip install "$dep" --no-cache-dir || warn "Failed to install $dep"
        done
    fi
    
    log "Python dependencies installation completed ✓"
}

# Create configuration files
create_configs() {
    log "Creating configuration files..."
    
    # Main settings
    cat > "$CONFIG_DIR/settings.json" << 'EOF'
{
    "general": {
        "wake_word": "jarvis",
        "name": "JARVIS",
        "version": "1.0.0",
        "debug": false
    },
    "voice": {
        "input": {
            "timeout": 5,
            "phrase_time_limit": 10,
            "ambient_duration": 1,
            "device_index": null
        },
        "output": {
            "rate": 180,
            "volume": 0.9,
            "voice_id": null
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
        "animations": true
    },
    "security": {
        "allowed_commands": [
            "ls", "pwd", "cat", "head", "tail", "grep", "find",
            "ps", "top", "df", "free", "uptime", "uname",
            "ping", "curl", "wget", "git", "python3", "pip3"
        ],
        "timeout": 30,
        "max_command_length": 200
    },
    "features": {
        "web_search": true,
        "wikipedia": true,
        "weather": false,
        "email": false,
        "calendar": false
    }
}
EOF
    
    # Audio configuration
    cat > "$CONFIG_DIR/audio_config.json" << 'EOF'
{
    "input": {
        "device_name": null,
        "sample_rate": 16000,
        "chunk_size": 1024,
        "channels": 1,
        "format": "int16"
    },
    "output": {
        "device_name": null,
        "volume": 0.8,
        "speed": 1.0
    },
    "processing": {
        "noise_reduction": true,
        "auto_gain": true,
        "echo_cancellation": false
    }
}
EOF
    
    # Security policies
    cat > "$CONFIG_DIR/security_config.json" << 'EOF'
{
    "command_whitelist": {
        "file_operations": ["ls", "pwd", "cat", "head", "tail", "grep", "find", "wc"],
        "system_info": ["ps", "top", "df", "free", "uptime", "uname", "whoami"],
        "network": ["ping", "curl", "wget", "traceroute"],
        "development": ["git", "python3", "pip3", "node", "npm"]
    },
    "forbidden_patterns": [
        "sudo", "su", "chmod 777", "rm -rf", "mkfs", "fdisk",
        "passwd", "useradd", "userdel", "systemctl", "service"
    ],
    "max_execution_time": 30,
    "max_output_size": 10000,
    "log_all_commands": true
}
EOF
    
    log "Configuration files created ✓"
}

# Create launcher scripts
create_launchers() {
    log "Creating launcher scripts..."
    
    # Main launcher
    cat > "$INSTALL_DIR/start_jarvis.sh" << EOF
#!/bin/bash

# JARVIS Voice Assistant Launcher
cd "$INSTALL_DIR"
source "$VENV_DIR/bin/activate"

if [[ -f "jarvis.py" ]]; then
    python3 jarvis.py "\$@"
else
    echo "Error: jarvis.py not found!"
    echo "Please ensure the main application file exists."
    exit 1
fi
EOF
    chmod +x "$INSTALL_DIR/start_jarvis.sh"
    
    # Audio test script
    cat > "$INSTALL_DIR/scripts/test_audio.sh" << 'EOF'
#!/bin/bash

echo "🎤 Testing JARVIS Audio System..."
echo "=================================="

# Test microphone
echo "Testing microphone (3 second recording)..."
if arecord -d 3 -f cd /tmp/test_mic.wav 2>/dev/null; then
    echo "✓ Microphone recording successful"
    
    # Test speakers
    echo "Testing speakers (playing back recording)..."
    if aplay /tmp/test_mic.wav 2>/dev/null; then
        echo "✓ Speaker playback successful"
    else
        echo "✗ Speaker playback failed"
    fi
    
    rm -f /tmp/test_mic.wav
else
    echo "✗ Microphone recording failed"
fi

# Test text-to-speech
echo "Testing text-to-speech..."
if command -v espeak &> /dev/null; then
    espeak "JARVIS audio test completed" 2>/dev/null
    echo "✓ Text-to-speech working"
else
    echo "✗ Text-to-speech not available"
fi

echo "Audio test completed!"
EOF
    chmod +x "$INSTALL_DIR/scripts/test_audio.sh"
    
    # Update script
    cat > "$INSTALL_DIR/scripts/update_jarvis.sh" << EOF
#!/bin/bash

echo "🔄 Updating JARVIS..."
cd "$INSTALL_DIR"

# Backup current config
if [[ -d "config" ]]; then
    cp -r config config_backup_\$(date +%Y%m%d_%H%M%S)
fi

# Pull latest changes
git pull origin main

# Update dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade -r requirements.txt

echo "✓ JARVIS updated successfully!"
EOF
    chmod +x "$INSTALL_DIR/scripts/update_jarvis.sh"
    
    log "Launcher scripts created ✓"
}

# Create desktop entry
create_desktop_entry() {
    log "Creating desktop entry..."
    
    # Create desktop file
    cat > "$HOME/.local/share/applications/jarvis-assistant.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS Voice Assistant
Comment=Your Personal AI Assistant
Exec=bash -c "cd '$INSTALL_DIR' && ./start_jarvis.sh"
Icon=$INSTALL_DIR/assets/jarvis_icon.png
Terminal=true
Categories=Utility;AudioVideo;
Keywords=voice;assistant;ai;jarvis;
StartupNotify=true
EOF
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
    fi
    
    log "Desktop entry created ✓"
}

# Create shell aliases
create_aliases() {
    log "Creating shell aliases..."
    
    # Add to bashrc
    if ! grep -q "JARVIS aliases" "$HOME/.bashrc"; then
        cat >> "$HOME/.bashrc" << EOF

# JARVIS aliases
alias jarvis='cd "$INSTALL_DIR" && ./start_jarvis.sh'
alias jarvis-test='cd "$INSTALL_DIR" && ./scripts/test_audio.sh'
alias jarvis-update='cd "$INSTALL_DIR" && ./scripts/update_jarvis.sh'
alias jarvis-config='cd "$INSTALL_DIR/config"'
alias jarvis-logs='cd "$INSTALL_DIR/logs" && tail -f jarvis.log'
EOF
    fi
    
    log "Shell aliases created ✓"
}

# Perform final checks
final_checks() {
    log "Performing final system checks..."
    
    # Check virtual environment
    if [[ -d "$VENV_DIR" ]]; then
        log "✓ Virtual environment created"
    else
        error "Virtual environment creation failed"
    fi
    
    # Check Python packages
    source "$VENV_DIR/bin/activate"
    if python3 -c "import speech_recognition, pyttsx3, rich" 2>/dev/null; then
        log "✓ Core Python packages installed"
    else
        warn "Some Python packages may not be properly installed"
    fi
    
    # Check audio system
    if command -v arecord &> /dev/null && command -v aplay &> /dev/null; then
        log "✓ Audio system available"
    else
        warn "Audio system may not be properly configured"
    fi
    
    log "Final checks completed ✓"
}

# Display installation summary
show_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                          🎉 Installation Complete!                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📍 Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${CYAN}🐍 Virtual Environment:${NC} $VENV_DIR"
    echo -e "${CYAN}⚙️  Configuration:${NC} $CONFIG_DIR"
    echo -e "${CYAN}📝 Logs:${NC} $LOGS_DIR"
    echo ""
    echo -e "${YELLOW}🚀 Quick Start Commands:${NC}"
    echo -e "   ${WHITE}jarvis${NC}                    # Start JARVIS"
    echo -e "   ${WHITE}jarvis-test${NC}               # Test audio system"
    echo -e "   ${WHITE}jarvis-config${NC}             # Open config directory"
    echo -e "   ${WHITE}jarvis-logs${NC}               # View logs"
    echo ""
    echo -e "${YELLOW}📖 Next Steps:${NC}"
    echo -e "   1. ${WHITE}Restart your terminal${NC} or run: ${CYAN}source ~/.bashrc${NC}"
    echo -e "   2. ${WHITE}Test your audio system${NC} with: ${CYAN}jarvis-test${NC}"
    echo -e "   3. ${WHITE}Start JARVIS${NC} with: ${CYAN}jarvis${NC}"
    echo -e "   4. ${WHITE}Say 'Jarvis' followed by your command${NC}"
    echo ""
    echo -e "${GREEN}🎤 Example Commands:${NC}"
    echo -e "   • ${WHITE}\"Jarvis, hello\"${NC}"
    echo -e "   • ${WHITE}\"Jarvis, what time is it?\"${NC}"
    echo -e "   • ${WHITE}\"Jarvis, search for Python tutorials\"${NC}"
    echo -e "   • ${WHITE}\"Jarvis, system status\"${NC}"
    echo ""
    echo -e "${PURPLE}📞 Support:${NC}"
    echo -e "   • Documentation: $INSTALL_DIR/docs/"
    echo -e "   • Issues: $REPO_URL/issues"
    echo -e "   • Discussions: $REPO_URL/discussions"
    echo ""
    echo -e "${CYAN}Thank you for choosing JARVIS! 🤖${NC}"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    log "Starting JARVIS Voice Assistant installation..."
    
    # Run installation steps
    check_system
    check_prerequisites
    install_system_deps
    setup_audio
    create_structure
    setup_venv
    install_python_deps
    create_configs
    create_launchers
    create_desktop_entry
    create_aliases
    final_checks
    
    show_summary
    
    log "Installation completed successfully! 🎉"
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted by user.${NC}"; exit 1' INT

# Run main function
main "$@"
