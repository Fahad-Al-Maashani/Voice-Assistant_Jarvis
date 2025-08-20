#!/bin/bash

# JARVIS Voice Assistant - Launcher Script
# Author: Fahad Al Maashani
# Description: Start JARVIS with proper environment and error handling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="JARVIS Voice Assistant"
PROJECT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/jarvis_env"
MAIN_SCRIPT="$PROJECT_ROOT/jarvis.py"
CONFIG_DIR="$PROJECT_ROOT/config"
LOGS_DIR="$PROJECT_ROOT/logs"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Print JARVIS banner
print_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

        Personal AI Assistant v1.0.0
        Starting up systems...

EOF
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "$MAIN_SCRIPT" ]]; then
        error "JARVIS main script not found at: $MAIN_SCRIPT"
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    local major_version=$(echo $python_version | cut -d'.' -f1)
    local minor_version=$(echo $python_version | cut -d'.' -f2)
    
    if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 8 ]]; then
        error "Python 3.8+ is required. Found: $python_version"
    fi
    
    log "✓ Python $python_version detected"
    
    # Check virtual environment
    if [[ ! -d "$VENV_PATH" ]]; then
        warn "Virtual environment not found. Creating one..."
        python3 -m venv "$VENV_PATH"
        log "✓ Virtual environment created"
    fi
    
    # Check configuration directory
    if [[ ! -d "$CONFIG_DIR" ]]; then
        warn "Configuration directory not found. Creating..."
        mkdir -p "$CONFIG_DIR"
        log "✓ Configuration directory created"
    fi
    
    # Check logs directory
    if [[ ! -d "$LOGS_DIR" ]]; then
        mkdir -p "$LOGS_DIR"
        log "✓ Logs directory created"
    fi
}

# Setup environment
setup_environment() {
    info "Setting up environment..."
    
    # Navigate to project root
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    if [[ -f "$VENV_PATH/bin/activate" ]]; then
        source "$VENV_PATH/bin/activate"
        log "✓ Virtual environment activated"
    else
        error "Virtual environment activation script not found"
    fi
    
    # Set Python path
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Set environment variables for JARVIS
    export JARVIS_HOME="$PROJECT_ROOT"
    export JARVIS_CONFIG="$CONFIG_DIR"
    export JARVIS_LOGS="$LOGS_DIR"
    
    log "✓ Environment variables set"
}

# Check Python dependencies
check_dependencies() {
    info "Checking Python dependencies..."
    
    local required_modules=(
        "speech_recognition"
        "pyttsx3"
        "rich"
        "requests"
        "googlesearch"
        "wikipedia"
        "psutil"
    )
    
    local missing_modules=()
    
    for module in "${required_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log "✓ $module available"
        else
            missing_modules+=("$module")
        fi
    done
    
    if [[ ${#missing_modules[@]} -gt 0 ]]; then
        warn "Missing Python modules: ${missing_modules[*]}"
        
        if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
            info "Installing missing dependencies..."
            pip install -r "$PROJECT_ROOT/requirements.txt" || error "Failed to install dependencies"
            log "✓ Dependencies installed"
        else
            error "requirements.txt not found. Please install dependencies manually."
        fi
    else
        log "✓ All required Python modules available"
    fi
}

# Check audio system
check_audio_system() {
    info "Checking audio system..."
    
    # Check audio devices
    if command -v arecord &> /dev/null; then
        if arecord -l | grep -q "card"; then
            log "✓ Audio input devices detected"
        else
            warn "No audio input devices found"
        fi
    else
        warn "arecord not available - audio recording may not work"
    fi
    
    if command -v aplay &> /dev/null; then
        if aplay -l | grep -q "card"; then
            log "✓ Audio output devices detected"
        else
            warn "No audio output devices found"
        fi
    else
        warn "aplay not available - audio playback may not work"
    fi
    
    # Check PulseAudio
    if pgrep -x "pulseaudio" > /dev/null; then
        log "✓ PulseAudio running"
    else
        warn "PulseAudio not running - starting..."
        pulseaudio --start --log-target=syslog || warn "Failed to start PulseAudio"
    fi
    
    # Check audio permissions
    if [[ -r /dev/snd/controlC0 ]]; then
        log "✓ Audio permissions OK"
    else
        warn "Audio permission issues detected"
        info "You may need to run: sudo usermod -a -G audio $USER"
    fi
}

# Check network connectivity
check_network() {
    info "Checking network connectivity..."
    
    if ping -c 1 google.com &> /dev/null; then
        log "✓ Internet connectivity available"
    else
        warn "No internet connectivity - some features may not work"
    fi
    
    # Check DNS resolution
    if nslookup google.com &> /dev/null; then
        log "✓ DNS resolution working"
    else
        warn "DNS resolution issues detected"
    fi
}

# Create default configuration if needed
create_default_config() {
    local settings_file="$CONFIG_DIR/settings.json"
    
    if [[ ! -f "$settings_file" ]]; then
        info "Creating default configuration..."
        
        cat > "$settings_file" << 'EOF'
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
    "features": {
        "web_search": true,
        "wikipedia": true,
        "weather": false,
        "email": false
    }
}
EOF
        log "✓ Default configuration created"
    fi
}

# Parse command line arguments
parse_arguments() {
    DEBUG_MODE=false
    VERBOSE_MODE=false
    CONFIG_OVERRIDE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug|-d)
                DEBUG_MODE=true
                shift
                ;;
            --verbose|-v)
                VERBOSE_MODE=true
                shift
                ;;
            --config|-c)
                CONFIG_OVERRIDE="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --version)
                echo "$PROJECT_NAME $PROJECT_VERSION"
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help information
show_help() {
    echo -e "${CYAN}$PROJECT_NAME $PROJECT_VERSION${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --debug      Enable debug mode"
    echo "  -v, --verbose    Enable verbose output"
    echo "  -c, --config     Specify custom config directory"
    echo "  -h, --help       Show this help message"
    echo "      --version    Show version information"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start JARVIS normally"
    echo "  $0 --debug
