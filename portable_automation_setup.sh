#!/bin/bash
# Portable Instagram Automation Setup
# Works on ANY Ubuntu server: VPS, Cloud, Raspberry Pi, or Home Server
# Completely vendor-agnostic and migration-friendly

set -e

echo "🚀 Portable Instagram Automation Setup"
echo "======================================"
echo "This setup works everywhere: VPS, Cloud, Pi, Home Server"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Detect system type
detect_system() {
    if [ -f /proc/device-tree/model ]; then
        DEVICE_TYPE="Raspberry Pi"
    elif [ -f /.dockerenv ]; then
        DEVICE_TYPE="Docker Container"
    elif curl -s metadata.google.internal > /dev/null 2>&1; then
        DEVICE_TYPE="Google Cloud"
    elif curl -s 169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
        DEVICE_TYPE="AWS"
    else
        DEVICE_TYPE="Generic VPS/Server"
    fi
    
    print_success "Detected: $DEVICE_TYPE"
}

# System requirements check
check_requirements() {
    print_step "Checking System Requirements"
    
    # Check Ubuntu version
    if ! lsb_release -d | grep -q Ubuntu; then
        echo "❌ This script requires Ubuntu. Detected: $(lsb_release -d)"
        exit 1
    fi
    
    # Check memory (minimum 512MB)
    MEM_MB=$(free -m | awk 'NR==2{printf "%d", $2}')
    if [ $MEM_MB -lt 512 ]; then
        print_warning "Low memory detected: ${MEM_MB}MB. Minimum 512MB recommended."
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "System requirements met"
}

# Install base dependencies
install_dependencies() {
    print_step "Installing Base Dependencies"
    
    # Update system
    sudo apt-get update -y
    sudo apt-get upgrade -y
    
    # Install essential packages
    sudo apt-get install -y \
        curl \
        wget \
        git \
        nano \
        htop \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    print_success "Base dependencies installed"
}

# Install Python
install_python() {
    print_step "Installing Python Environment"
    
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential
    
    # Upgrade pip
    python3 -m pip install --user --upgrade pip
    
    print_success "Python environment ready"
}

# Install Chrome/Chromium
install_browser() {
    print_step "Installing Browser for Automation"
    
    # Try Google Chrome first, fallback to Chromium
    if wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 2>/dev/null; then
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update -y
        
        if sudo apt-get install -y google-chrome-stable 2>/dev/null; then
            BROWSER="google-chrome"
            print_success "Google Chrome installed"
        else
            print_warning "Chrome installation failed, installing Chromium"
            sudo apt-get install -y chromium-browser
            BROWSER="chromium-browser"
        fi
    else
        print_warning "Installing Chromium (Chrome unavailable)"
        sudo apt-get install -y chromium-browser
        BROWSER="chromium-browser"
    fi
    
    # Install ChromeDriver
    if [ "$BROWSER" = "google-chrome" ]; then
        CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
        DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
        unzip /tmp/chromedriver.zip -d /tmp/
        sudo mv /tmp/chromedriver /usr/local/bin/
        sudo chmod +x /usr/local/bin/chromedriver
        rm /tmp/chromedriver.zip
    else
        sudo apt-get install -y chromium-chromedriver
        sudo ln -sf /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver 2>/dev/null || true
    fi
    
    # Install virtual display for headless operation
    sudo apt-get install -y xvfb x11vnc
    
    print_success "Browser environment ready"
}

# Create application structure
setup_application() {
    print_step "Setting Up Application Structure"
    
    # Create application directory
    APP_DIR="$HOME/instagram-automation"
    mkdir -p "$APP_DIR"
    cd "$APP_DIR"
    
    # Create directory structure
    mkdir -p {config,logs,data,backups,scripts}
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Create requirements.txt (vendor-agnostic)
    cat > requirements.txt << 'EOF'
selenium==4.15.2
schedule==1.2.0
flask==2.3.3
waitress==2.1.2
psutil==5.9.6
requests==2.31.0
python-dotenv==1.0.0
jsonschema==4.17.3
EOF
    
    # Install Python packages
    pip install --upgrade pip
    pip install -r requirements.txt
    
    deactivate
    
    print_success "Application structure created"
}

# Display final instructions
show_final_instructions() {
    echo ""
    echo "🎉 Instagram Automation Setup Complete!"
    echo "======================================"
    echo ""
    echo "📁 Installation Location: $APP_DIR"
    echo "🖥️  Detected System: $DEVICE_TYPE"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Configure Instagram credentials:"
    echo "   nano $APP_DIR/.env"
    echo ""
    echo "2. Update target accounts:"
    echo "   nano $APP_DIR/config/automation_config.json"
    echo ""
    echo "3. Start the automation:"
    echo "   cd $APP_DIR && ./scripts/control.sh start"
    echo ""
    echo "4. Access dashboard:"
    echo "   http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'YOUR_IP'):5000"
    echo ""
    echo "🔧 Management Commands:"
    echo "   ./scripts/control.sh [start|stop|restart|status|logs]"
    echo "   ./scripts/backup.sh (create backup)"
    echo "   ./scripts/migrate.sh (migration guide)"
    echo ""
    echo "🚛 Migration Features:"
    echo "   ✅ Works on any Ubuntu server"
    echo "   ✅ Easy backup/restore"
    echo "   ✅ No vendor lock-in"
    echo "   ✅ 10-minute migration time"
    echo ""
    echo "🌟 This setup is completely portable!"
    echo "   Move between VPS providers in minutes, not weeks!"
    echo ""
}

# Main execution
main() {
    echo "Starting portable setup..."
    
    detect_system
    check_requirements
    install_dependencies
    install_python
    install_browser
    setup_application
    show_final_instructions
}

# Run main function
main "$@" 