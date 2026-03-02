#!/bin/bash
# Content Idea Generator - Installation Script
# This script sets up the Content Idea Generator skill for OpenClaw

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SKILL_NAME="content-idea-generator"
CONFIG_DIR="${HOME}/.openclaw/${SKILL_NAME}"
DEFAULT_CONFIG_URL="https://raw.githubusercontent.com/openclaw/skills/main/content-idea-generator/config/default_config.yaml"

# Helper functions
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║        Content Idea Generator - Installation                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}➤${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Check Python version
check_python() {
    print_step "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "   Please install Python 3.9 or higher: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "Python $PYTHON_VERSION is too old (requires 3.9+)"
        echo "   Please upgrade Python: https://www.python.org/downloads/"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected (✓ meets requirement >= 3.9)"
}

# Install pip dependencies
install_dependencies() {
    print_step "Installing pip dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found in current directory"
        echo "   Please run this script from the skill root directory"
        exit 1
    fi
    
    # Install core dependencies
    pip3 install -r requirements.txt --quiet
    
    print_success "Dependencies installed successfully"
}

# Check optional dependencies
check_optional_deps() {
    print_step "Checking optional dependencies..."
    
    # Check tesseract-ocr
    if command -v tesseract &> /dev/null; then
        print_success "tesseract-ocr is installed"
    else
        print_warning "tesseract-ocr is not installed"
        echo "   OCR functionality for screenshots will not be available"
        echo ""
        echo "   To install tesseract-ocr:"
        echo "     Ubuntu/Debian: sudo apt-get install tesseract-ocr"
        echo "     macOS:         brew install tesseract"
        echo "     Windows:       https://github.com/UB-Mannheim/tesseract/wiki"
        echo ""
    fi
    
    # Check whisper.cpp (optional)
    if command -v whisper-cli &> /dev/null || command -v whisper &> /dev/null; then
        print_success "whisper.cpp is installed"
    else
        print_warning "whisper.cpp is not installed"
        echo "   Voice input functionality will not be available"
        echo "   Install from: https://github.com/ggerganov/whisper.cpp"
        echo ""
    fi
}

# Create config directory
setup_config() {
    print_step "Setting up configuration directory..."
    
    mkdir -p "${CONFIG_DIR}"
    print_success "Created config directory: ${CONFIG_DIR}"
    
    # Check if default config exists in the repo
    if [ -f "config/default_config.yaml" ]; then
        if [ ! -f "${CONFIG_DIR}/config.yaml" ]; then
            cp "config/default_config.yaml" "${CONFIG_DIR}/config.yaml"
            print_success "Copied default configuration"
        else
            print_info "Configuration already exists, skipping copy"
        fi
    else
        # Create a minimal default config
        if [ ! -f "${CONFIG_DIR}/config.yaml" ]; then
            cat > "${CONFIG_DIR}/config.yaml" << 'EOF'
# Content Idea Generator Configuration
database:
  path: "~/.openclaw/content-idea-generator/library.db"

# Optional: Whisper for voice input
whisper:
  enabled: false
  model: "base"
  path: "whisper-cli"

# Report settings
report:
  schedule: "daily"
  time: "09:00"

# Optional: Obsidian export
obsidian:
  export_path: "~/Obsidian/Content Ideas"
EOF
            print_success "Created default configuration"
        else
            print_info "Configuration already exists"
        fi
    fi
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    # Check if main modules can be imported
    if python3 -c "import sys; sys.path.insert(0, 'src'); from database import ContentDatabase" 2>/dev/null; then
        print_success "Core modules import successfully"
    else
        print_warning "Could not verify module imports (this is usually OK)"
    fi
    
    # Check database directory
    if [ -d "${CONFIG_DIR}" ]; then
        print_success "Config directory is accessible"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Complete! 🎉                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo ""
    echo "  1. ${YELLOW}Configure the skill:${NC}"
    echo "     Edit: ${CONFIG_DIR}/config.yaml"
    echo ""
    echo "  2. ${YELLOW}Test the installation:${NC}"
    echo "     python3 -c \"from src.database import ContentDatabase; print('OK')\""
    echo ""
    echo "  3. ${YELLOW}Run tests:${NC}"
    echo "     pytest tests/ -v"
    echo ""
    echo "  4. ${YELLOW}Start capturing ideas:${NC}"
    echo "     Use commands: /capture, /voice, /search, /report"
    echo ""
    echo -e "${CYAN}Documentation:${NC}"
    echo "  • SKILL.md - Full documentation and usage guide"
    echo "  • README.md - Project overview"
    echo ""
    echo -e "${CYAN}Support:${NC}"
    echo "  • GitHub: https://github.com/openclaw/skills"
    echo "  • Issues: https://github.com/openclaw/skills/issues"
    echo ""
}

# Main installation flow
main() {
    print_header
    
    check_python
    install_dependencies
    check_optional_deps
    setup_config
    verify_installation
    
    print_next_steps
}

# Run main function
main "$@"
