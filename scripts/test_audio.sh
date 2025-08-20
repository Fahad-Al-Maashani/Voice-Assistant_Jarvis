#!/bin/bash

# JARVIS Voice Assistant - Audio System Test
# Author: Fahad Al Maashani
# Description: Comprehensive audio system testing for JARVIS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Test configuration
TEST_DURATION=3
TEST_FILE="/tmp/jarvis_audio_test.wav"
SAMPLE_RATE=44100
CHANNELS=1

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Print test banner
print_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                🎤 JARVIS Audio System Test 🔊                ║
║                                                              ║
║           Testing microphone and speaker functionality       ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo ""
}

# Check if running with proper permissions
check_permissions() {
    info "Checking audio permissions..."
    
    # Check if user is in audio group
    if groups | grep -q audio; then
        success "✓ User is in audio group"
    else
        warn "User not in audio group. You may need to run:"
        echo "  sudo usermod -a -G audio $USER"
        echo "  Then logout and login again"
    fi
    
    # Check audio device permissions
    if [[ -r /dev/snd/controlC0 ]]; then
        success "✓ Audio device permissions OK"
    else
        warn "Audio device permission issues detected"
    fi
}

# Test system audio tools
test_audio_tools() {
    info "Testing audio system tools..."
    
    local tools=("arecord" "aplay" "pactl" "alsamixer")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            success "✓ $tool available"
        else
            missing_tools+=("$tool")
            warn "✗ $tool not found"
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        warn "Missing audio tools: ${missing_tools[*]}"
        info "Install with: sudo apt install alsa-utils pulseaudio-utils"
    fi
}

# List audio devices
list_audio_devices() {
    info "Detecting audio devices..."
    echo ""
    
    # List recording devices
    echo -e "${CYAN}📥 Audio Input Devices (Microphones):${NC}"
    if command -v arecord &> /dev/null; then
        if arecord -l 2>/dev/null | grep -q "card"; then
            arecord -l | grep -E "(card|device)" | while read line; do
                echo "  $line"
            done
        else
            warn "No audio input devices detected"
        fi
    else
        error "arecord not available"
    fi
    
    echo ""
    
    # List playback devices
    echo -e "${CYAN}📤 Audio Output Devices (Speakers):${NC}"
    if command -v aplay &> /dev/null; then
        if aplay -l 2>/dev/null | grep -q "card"; then
            aplay -l | grep -E "(card|device)" | while read line; do
                echo "  $line"
            done
        else
            warn "No audio output devices detected"
        fi
    else
        error "aplay not available"
    fi
    
    echo ""
    
    # PulseAudio devices
    if command -v pactl &> /dev/null; then
        echo -e "${CYAN}🔊 PulseAudio Sources (Input):${NC}"
        pactl list short sources | while read line; do
            echo "  $line"
        done
        
        echo ""
        echo -e "${CYAN}🔈 PulseAudio Sinks (Output):${NC}"
        pactl list short sinks | while read line; do
            echo "  $line"
        done
    fi
    
    echo ""
}

# Test PulseAudio
test_pulseaudio() {
    info "Testing PulseAudio system..."
    
    # Check if PulseAudio is running
    if pgrep -x "pulseaudio" > /dev/null; then
        success "✓ PulseAudio is running"
        
        # Get PulseAudio version
        if command -v pulseaudio &> /dev/null; then
            local version=$(pulseaudio --version | head -1)
            info "Version: $version"
        fi
        
        # Test PulseAudio info
        if pactl info &> /dev/null; then
            success "✓ PulseAudio responding to commands"
        else
            warn "PulseAudio not responding properly"
        fi
        
    else
        warn "PulseAudio not running"
        info "Attempting to start PulseAudio..."
        
        if pulseaudio --start --log-target=syslog; then
            success "✓ PulseAudio started successfully"
        else
            error "Failed to start PulseAudio"
        fi
    fi
}

# Test microphone recording
test_microphone() {
    info "Testing microphone recording..."
    
    # Check if microphone devices exist
    if ! arecord -l 2>/dev/null | grep -q "card"; then
        error "No microphone devices detected"
        return 1
    fi
    
    # Clean up any existing test file
    rm -f "$TEST_FILE"
    
    echo ""
    echo -e "${YELLOW}🎤 MICROPHONE TEST${NC}"
    echo "Recording $TEST_DURATION seconds of audio..."
    echo "Please speak into your microphone or make some noise."
    echo ""
    
    # Countdown
    for i in {3..1}; do
        echo -n "Starting in $i... "
        sleep 1
        echo ""
    done
    
    echo -e "${GREEN}🔴 RECORDING NOW - Speak into your microphone!${NC}"
    
    # Record audio
    if arecord -d $TEST_DURATION -f cd -t wav "$TEST_FILE" 2>/dev/null; then
        success "✓ Audio recording completed"
        
        # Check file size
        if [[ -f "$TEST_FILE" ]]; then
            local file_size=$(stat -c%s "$TEST_FILE" 2>/dev/null || echo "0")
            if [[ $file_size -gt 1000 ]]; then
                success "✓ Audio data captured ($file_size bytes)"
                return 0
            else
                warn "Audio file too small - microphone may not be working"
                return 1
            fi
        else
            error "Audio file not created"
            return 1
        fi
    else
        error "Failed to record audio"
        return 1
    fi
}

# Test speaker playback
test_speakers() {
    info "Testing speaker playback..."
    
    # Check if playback devices exist
    if ! aplay -l 2>/dev/null | grep -q "card"; then
        error "No speaker devices detected"
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}🔊 SPEAKER TEST${NC}"
    
    # Test with recorded audio if available
    if [[ -f "$TEST_FILE" ]]; then
        echo "Playing back your recorded audio..."
        echo "You should hear what you just recorded."
        echo ""
        
        if aplay "$TEST_FILE" 2>/dev/null; then
            success "✓ Audio playback completed"
            
            echo ""
            read -p "Did you hear the playback? (y/n): " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                success "✓ Speaker test passed"
                return 0
            else
                warn "Speaker test failed - no audio heard"
                return 1
            fi
        else
            error "Failed to play audio"
            return 1
        fi
    else
        # Generate test tone if no recording available
        info "Generating test tone..."
        
        if command -v speaker-test &> /dev/null; then
            echo "Playing test tone for 3 seconds..."
            timeout 3s speaker-test -t wav -c 2 &>/dev/null || true
            
            echo ""
            read -p "Did you hear the test tone? (y/n): " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                success "✓ Speaker test passed"
                return 0
            else
                warn "Speaker test failed - no audio heard"
                return 1
            fi
        else
            warn "Cannot generate test tone - speaker-test not available"
            return 1
        fi
    fi
}

# Test text-to-speech
test_tts() {
    info "Testing text-to-speech engines..."
    
    local tts_engines=("espeak" "festival" "spd-say")
    local working_engines=()
    
    for engine in "${tts_engines[@]}"; do
        if command -v "$engine" &> /dev/null; then
            echo ""
            echo -e "${CYAN}Testing $engine...${NC}"
            
            case $engine in
                "espeak")
                    if echo "JARVIS audio test using espeak" | espeak 2>/dev/null; then
                        working_engines+=("$engine")
                        success "✓ $engine working"
                    else
                        warn "✗ $engine failed"
                    fi
                    ;;
                "festival")
                    if echo "JARVIS audio test using festival" | festival --tts 2>/dev/null; then
                        working_engines+=("$engine")
                        success "✓ $engine working"
                    else
                        warn "✗ $engine failed"
                    fi
                    ;;
                "spd-say")
                    if spd-say "JARVIS audio test using speech dispatcher" 2>/dev/null; then
                        working_engines+=("$engine")
                        success "✓ $engine working"
                    else
                        warn "✗ $engine failed"
                    fi
                    ;;
            esac
            
            sleep 1
        else
            info "$engine not installed"
        fi
    done
    
    if [[ ${#working_engines[@]} -gt 0 ]]; then
        success "Working TTS engines: ${working_engines[*]}"
        
        echo ""
        read -p "Did you hear the text-to-speech? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            success "✓ Text-to-speech test passed"
            return 0
        else
            warn "Text-to-speech test failed"
            return 1
        fi
    else
        error "No working text-to-speech engines found"
        info "Install with: sudo apt install espeak festival speech-dispatcher"
        return 1
    fi
}

# Test Python audio modules
test_python_audio() {
    info "Testing Python audio modules..."
    
    # Test if we're in a virtual environment
    local python_cmd="python3"
    if [[ -n "$VIRTUAL_ENV" ]]; then
        info "Using virtual environment: $VIRTUAL_ENV"
    fi
    
    # Test speech recognition module
    echo ""
    echo -e "${CYAN}Testing speech_recognition module...${NC}"
    if $python_cmd -c "import speech_recognition; print('✓ speech_recognition imported successfully')" 2>/dev/null; then
        success "✓ speech_recognition module available"
    else
        error "speech_recognition module not available"
        info "Install with: pip install SpeechRecognition"
    fi
    
    # Test pyttsx3 module
    echo ""
    echo -e "${CYAN}Testing pyttsx3 module...${NC}"
    if $python_cmd -c "import pyttsx3; engine = pyttsx3.init(); print('✓ pyttsx3 initialized successfully')" 2>/dev/null; then
        success "✓ pyttsx3 module available"
        
        # Test TTS with pyttsx3
        echo "Testing pyttsx3 speech synthesis..."
        if $python_cmd -c "
import pyttsx3
try:
    engine = pyttsx3.init()
    engine.say('JARVIS python text to speech test')
    engine.runAndWait()
    print('✓ pyttsx3 speech synthesis working')
except Exception as e:
    print(f'✗ pyttsx3 speech synthesis failed: {e}')
" 2>/dev/null; then
            
            echo ""
            read -p "Did you hear the Python TTS? (y/n): " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                success "✓ Python TTS test passed"
            else
                warn "Python TTS test failed"
            fi
        fi
    else
        error "pyttsx3 module not available"
        info "Install with: pip install pyttsx3"
    fi
    
    # Test pyaudio module
    echo ""
    echo -e "${CYAN}Testing pyaudio module...${NC}"
    if $python_cmd -c "import pyaudio; print('✓ pyaudio imported successfully')" 2>/dev/null; then
        success "✓ pyaudio module available"
    else
        warn "pyaudio module not available"
        info "Install with: pip install pyaudio"
        info "If installation fails, try: sudo apt install portaudio19-dev"
    fi
}

# Audio level test
test_audio_levels() {
    info "Testing audio levels..."
    
    if command -v pactl &> /dev/null; then
        echo ""
        echo -e "${CYAN}Current Audio Levels:${NC}"
        
        # Get default sink (output) volume
        local default_sink=$(pactl get-default-sink)
        if [[ -n "$default_sink" ]]; then
            local sink_volume=$(pactl get-sink-volume "$default_sink" | grep -oP '\d+%' | head -1)
            echo "  🔊 Output Volume: $sink_volume"
        fi
        
        # Get default source (input) volume
        local default_source=$(pactl get-default-source)
        if [[ -n "$default_source" ]]; then
            local source_volume=$(pactl get-source-volume "$default_source" | grep -oP '\d+%' | head -1)
            echo "  🎤 Input Volume: $source_volume"
        fi
        
        # Check if muted
        if pactl get-sink-mute "$default_sink" | grep -q "yes"; then
            warn "⚠️  Output is muted!"
        fi
        
        if pactl get-source-mute "$default_source" | grep -q "yes"; then
            warn "⚠️  Input is muted!"
        fi
    fi
    
    echo ""
    info "If audio levels are too low/high, use: alsamixer or pavucontrol"
}

# Cleanup function
cleanup() {
    info "Cleaning up test files..."
    rm -f "$TEST_FILE"
}

# Generate test report
generate_report() {
    local mic_status=$1
    local speaker_status=$2
    local tts_status=$3
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     🎤 AUDIO TEST REPORT 🔊                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # System information
    echo -e "${YELLOW}System Information:${NC}"
    echo "  OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')"
    echo "  Audio System: $(if pgrep pulseaudio >/dev/null; then echo 'PulseAudio'; else echo 'ALSA'; fi)"
    echo "  Date: $(date)"
    echo ""
    
    # Test results
    echo -e "${YELLOW}Test Results:${NC}"
    
    if [[ $mic_status -eq 0 ]]; then
        echo -e "  🎤 Microphone: ${GREEN}✓ PASS${NC}"
    else
        echo -e "  🎤 Microphone: ${RED}✗ FAIL${NC}"
    fi
    
    if [[ $speaker_status -eq 0 ]]; then
        echo -e "  🔊 Speakers: ${GREEN}✓ PASS${NC}"
    else
        echo -e "  🔊 Speakers: ${RED}✗ FAIL${NC}"
    fi
    
    if [[ $tts_status -eq 0 ]]; then
        echo -e "  🗣️  Text-to-Speech: ${GREEN}✓ PASS${NC}"
    else
        echo -e "  🗣️  Text-to-Speech: ${RED}✗ FAIL${NC}"
    fi
    
    echo ""
    
    # Overall status
    if [[ $mic_status -eq 0 && $speaker_status -eq 0 ]]; then
        echo -e "${GREEN}🎉 JARVIS AUDIO SYSTEM READY!${NC}"
        echo "Your system is ready to run JARVIS Voice Assistant."
    else
        echo -e "${YELLOW}⚠️  AUDIO ISSUES DETECTED${NC}"
        echo "Please fix the issues above before running JARVIS."
        
        echo ""
        echo -e "${CYAN}Troubleshooting Tips:${NC}"
        if [[ $mic_status -ne 0 ]]; then
            echo "  🎤 Microphone issues:"
            echo "    - Check microphone connection"
            echo "    - Verify microphone is not muted"
            echo "    - Run: alsamixer to adjust levels"
            echo "    - Check permissions: sudo usermod -a -G audio $USER"
        fi
        
        if [[ $speaker_status -ne 0 ]]; then
            echo "  🔊 Speaker issues:"
            echo "    - Check speaker/headphone connection"
            echo "    - Verify speakers are not muted"
            echo "    - Run: alsamixer to adjust levels"
            echo "    - Try different audio output device"
        fi
        
        if [[ $tts_status -ne 0 ]]; then
            echo "  🗣️  Text-to-Speech issues:"
            echo "    - Install TTS engines: sudo apt install espeak festival"
            echo "    - Check audio output is working"
            echo "    - Verify no audio conflicts"
        fi
    fi
    
    echo ""
}

# Main test function
main() {
    print_banner
    
    # Set up cleanup on exit
    trap cleanup EXIT
    
    # Initialize test results
    local mic_result=1
    local speaker_result=1
    local tts_result=1
    
    # Run tests
    check_permissions
    test_audio_tools
    list_audio_devices
    test_pulseaudio
    test_audio_levels
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    INTERACTIVE TESTS                          ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    
    # Interactive tests
    if test_microphone; then
        mic_result=0
    fi
    
    if test_speakers; then
        speaker_result=0
    fi
    
    if test_tts; then
        tts_result=0
    fi
    
    # Test Python modules
    test_python_audio
    
    # Generate final report
    generate_report $mic_result $speaker_result $tts_result
    
    # Return appropriate exit code
    if [[ $mic_result -eq 0 && $speaker_result -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}Audio test interrupted${NC}"; cleanup; exit 1' INT

# Run main function
main "$@"
