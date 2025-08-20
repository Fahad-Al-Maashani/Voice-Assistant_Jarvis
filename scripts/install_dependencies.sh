#!/bin/bash

# JARVIS Voice Assistant - System Dependencies Installer
# Author: Fahad Al Maashani
# Description: Install all required system dependencies for JARVIS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║           JARVIS System Dependencies Installer         ║"
    echo "║                Installing Required Packages            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user."
    fi
}

# Check distribution
check_distribution() {
    log "Checking Linux distribution..."
    
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        log "Detected: $PRETTY_NAME"
    else
        error "Cannot determine Linux distribution"
    fi
    
    # Check if it's Ubuntu/Debian based
    if ! command -v apt &> /dev/null; then
        error "This script requires apt package manager (Ubuntu/Debian)"
    fi
}

# Update package repositories
update_repositories() {
    log "Updating package repositories..."
    
    # Update package lists
    sudo apt update -qq || error "Failed to update package repositories"
    
    log "Package repositories updated successfully"
}

# Install system packages
install_system_packages() {
    log "Installing system packages..."
    
    # Core development packages
    local dev_packages=(
        "build-essential"
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "pkg-config"
        "cmake"
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
    
    # Audio packages
    local audio_packages=(
        "portaudio19-dev"
        "libasound2-dev"
        "libportaudio2"
        "libportaudiocpp0"
        "ffmpeg"
        "alsa-utils"
        "pulseaudio"
        "pulseaudio-utils"
        "pavucontrol"
    )
    
    # Text-to-speech packages
    local tts_packages=(
        "espeak"
        "espeak-data"
        "festival"
        "speech-dispatcher"
        "speech-dispatcher-espeak"
    )
    
    # Network and utility packages
    local utility_packages=(
        "net-tools"
        "traceroute"
        "iputils-ping"
        "dnsutils"
        "htop"
        "tree"
        "vim"
        "nano"
    )
    
    # Multimedia packages
    local multimedia_packages=(
        "libavcodec-dev"
        "libavformat-dev"
        "libswscale-dev"
        "libgstreamer1.0-dev"
        "libgstreamer-plugins-base1.0-dev"
    )
    
    # Combine all packages
    local all_packages=(
        "${dev_packages[@]}"
        "${audio_packages[@]}"
        "${tts_packages[@]}"
        "${utility_packages[@]}"
        "${multimedia_packages[@]}"
    )
    
    log "Installing ${#all_packages[@]} packages..."
    
    # Install packages in batches to handle failures gracefully
    local failed_packages=()
    
    for package in "${all_packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log "✓ $package already installed"
        else
            log "Installing $package..."
            if sudo apt install -y "$package" &>/dev/null; then
                log "✓ $package installed successfully"
            else
                warn "✗ Failed to install $package"
                failed_packages+=("$package")
            fi
        fi
    done
    
    # Report failed packages
    if [[ ${#failed_packages[@]} -gt 0 ]]; then
        warn "The following packages failed to install:"
        for package in "${failed_packages[@]}"; do
            echo "  - $package"
        done
        warn "JARVIS may still work, but some features might be limited."
    else
        log "All packages installed successfully!"
    fi
}

# Install Python development headers
install_python_headers() {
    log "Installing Python development headers..."
    
    # Get Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    local python_packages=(
        "python${PYTHON_VERSION}-dev"
        "python3-setuptools"
        "python3-wheel"
        "python3-distutils"
    )
    
    for package in "${python_packages[@]}"; do
        if sudo apt install -y "$package" &>/dev/null; then
            log "✓ $package installed"
        else
            warn "Could not install $package, continuing..."
        fi
    done
}

# Setup audio system
setup_audio_system() {
    log "Configuring audio system..."
    
    # Add user to audio group
    sudo usermod -a -G audio "$USER"
    log "✓ User added to audio group"
    
    # Start PulseAudio if not running
    if ! pgrep -x "pulseaudio" > /dev/null; then
        log "Starting PulseAudio..."
        pulseaudio --start --log-target=syslog
    else
        log "✓ PulseAudio already running"
    fi
    
    # Create PulseAudio config directory
    mkdir -p "$HOME/.config/pulse"
    
    # Set audio permissions
    if [[ -d /dev/snd ]]; then
        sudo chmod -R 666 /dev/snd/ 2>/dev/null || true
        log "✓ Audio device permissions set"
    fi
    
    log "Audio system configuration completed"
}

# Install additional repositories
install_additional_repos() {
    log "Adding additional repositories..."
    
    # Add deadsnakes PPA for newer Python versions (if needed)
    if [[ "$VERSION" == "20.04" ]]; then
        log "Adding deadsnakes PPA for Ubuntu 20.04..."
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt update -qq
    fi
    
    # Add multimedia codecs repository
    if ! dpkg -l | grep -q ubuntu-restricted-extras; then
        log "Installing multimedia codecs..."
        echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | sudo debconf-set-selections
        sudo apt install -y ubuntu-restricted-extras &>/dev/null || warn "Could not install multimedia codecs"
    fi
}

# Verify installations
verify_installations() {
    log "Verifying installations..."
    
    # Check Python
    if python3 --version &>/dev/null; then
        log "✓ Python3: $(python3 --version)"
    else
        error "Python3 verification failed"
    fi
    
    # Check pip
    if python3 -m pip --version &>/dev/null; then
        log "✓ pip: $(python3 -m pip --version | cut -d' ' -f1,2)"
    else
        error "pip verification failed"
    fi
    
    # Check audio tools
    if command -v arecord &>/dev/null && command -v aplay &>/dev/null; then
        log "✓ Audio tools (arecord/aplay) available"
    else
        warn "Audio tools may not be properly installed"
    fi
    
    # Check text-to-speech
    if command -v espeak &>/dev/null; then
        log "✓ Text-to-speech (espeak) available"
    else
        warn "Text-to-speech may not be available"
    fi
    
    # Check build tools
    if command -v gcc &>/dev/null && command -v make &>/dev/null; then
        log "✓ Build tools available"
    else
        warn "Build tools may not be properly installed"
    fi
    
    log "Installation verification completed"
}

# Clean up
cleanup_installation() {
    log "Cleaning up..."
    
    # Clean package cache
    sudo apt autoremove -y &>/dev/null || true
    sudo apt autoclean &>/dev/null || true
    
    # Update locate database
    if command -v updatedb &>/dev/null; then
        sudo updatedb &>/dev/null || true
    fi
    
    log "Cleanup completed"
}

# Create system shortcuts
create_shortcuts() {
    log "Creating system shortcuts..."
    
    # Create useful aliases
    local aliases_file="$HOME/.jarvis_aliases"
    
    cat > "$aliases_file" << 'EOF'
# JARVIS Audio Shortcuts
alias audio-test='arecord -d 3 /tmp/test.wav && aplay /tmp/test.wav && rm /tmp/test.wav'
alias audio-devices='arecord -l && echo "--- Playback Devices ---" && aplay -l'
alias audio-mixer='alsamixer'
alias audio-control='pavucontrol'

# JARVIS System Shortcuts
alias jarvis-deps='bash scripts/install_dependencies.sh'
alias jarvis-test='bash scripts/test_audio.sh'
alias jarvis-start='bash scripts/start_jarvis.sh'

# JARVIS Development Shortcuts
alias jarvis-logs='tail -f logs/jarvis*.log'
alias jarvis-config='cd config && ls -la'
alias jarvis-debug='python3 jarvis.py --debug'
EOF
    
    # Add to bashrc if not already present
    if ! grep -q "source.*jarvis_aliases" "$HOME/.bashrc"; then
        echo "" >> "$HOME/.bashrc"
        echo "# JARVIS aliases" >> "$HOME/.bashrc"
        echo "source $aliases_file" >> "$HOME/.bashrc"
        log "✓ JARVIS aliases added to .bashrc"
    fi
    
    log "System shortcuts created"
}

# Test installations
test_critical_components() {
    log "Testing critical components..."
    
    # Test Python imports
    log "Testing Python module availability..."
    
    python3 -c "
import sys
import subprocess
import json
import time
import threading
print('✓ Core Python modules available')
"
    
    # Test audio system
    if command -v arecord &>/dev/null; then
        log "Testing audio recording capability..."
        timeout 2s arecord -d 1 -f cd /tmp/jarvis_test.wav &>/dev/null || warn "Audio recording test failed"
        rm -f /tmp/jarvis_test.wav
    fi
    
    # Test text-to-speech
    if command -v espeak &>/dev/null; then
        log "Testing text-to-speech..."
        echo "JARVIS installation test" | espeak &>/dev/null || warn "TTS test failed"
    fi
    
    log "Component testing completed"
}

# Display installation summary
show_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              System Dependencies Installed!            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📦 Installed Components:${NC}"
    echo -e "   ✓ Python 3 development environment"
    echo -e "   ✓ Audio system (PortAudio, ALSA, PulseAudio)"
    echo -e "   ✓ Text-to-speech engines (espeak, festival)"
    echo -e "   ✓ Build tools and dependencies"
    echo -e "   ✓ Network and utility packages"
    echo -e "   ✓ Multimedia codecs and libraries"
    echo ""
    echo -e "${YELLOW}🔧 Next Steps:${NC}"
    echo -e "   1. ${BLUE}Restart your terminal${NC} or run: ${CYAN}source ~/.bashrc${NC}"
    echo -e "   2. ${BLUE}Install Python packages${NC} with: ${CYAN}pip install -r requirements.txt${NC}"
    echo -e "   3. ${BLUE}Test audio system${NC} with: ${CYAN}bash scripts/test_audio.sh${NC}"
    echo -e "   4. ${BLUE}Start JARVIS${NC} with: ${CYAN}bash scripts/start_jarvis.sh${NC}"
    echo ""
    echo -e "${YELLOW}🎤 Audio Configuration:${NC}"
    echo -e "   • Run ${CYAN}audio-test${NC} to test microphone and speakers"
    echo -e "   • Run ${CYAN}audio-devices${NC} to list available audio devices"
    echo -e "   • Run ${CYAN}audio-mixer${NC} to adjust audio levels"
    echo ""
    echo -e "${GREEN}System dependencies installation completed successfully!${NC}"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    log "Starting JARVIS system dependencies installation..."
    
    # Pre-installation checks
    check_root
    check_distribution
    
    # Installation steps
    update_repositories
    install_additional_repos
    install_system_packages
    install_python_headers
    setup_audio_system
    create_shortcuts
    verify_installations
    test_critical_components
    cleanup_installation
    
    show_summary
    
    log "System dependencies installation completed successfully!"
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted by user.${NC}"; exit 1' INT

# Run main function
main "$@"
