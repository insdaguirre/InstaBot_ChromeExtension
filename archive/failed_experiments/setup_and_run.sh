#!/bin/bash

# Instagram Bot Setup and Execution Script
# Optimized for parallel execution with 6 CPU cores

echo "🚀 Instagram Bot Setup & Execution Script"
echo "==========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Python 3 and pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to latest version
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install required packages with parallel processing
echo "📥 Installing required packages with parallel processing..."
pip install --upgrade -r requirements.txt --use-pep517 --no-cache-dir

# Install ChromeDriver for macOS (if not already installed)
echo "🌐 Setting up ChromeDriver..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v chromedriver &> /dev/null; then
        echo "📦 Installing ChromeDriver via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install --cask chromedriver
            echo "✅ ChromeDriver installed"
            
            # Remove quarantine attribute (common macOS security issue)
            echo "🔐 Removing quarantine attribute from ChromeDriver..."
            sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver 2>/dev/null || true
            chmod +x /usr/local/bin/chromedriver 2>/dev/null || true
            echo "✅ ChromeDriver permissions fixed"
        else
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    else
        echo "✅ ChromeDriver already installed"
        # Still try to fix permissions
        sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver 2>/dev/null || true
        chmod +x /usr/local/bin/chromedriver 2>/dev/null || true
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "📦 ChromeDriver will be managed automatically by webdriver-manager"
else
    # Windows or other
    echo "📦 ChromeDriver will be managed automatically by webdriver-manager"
fi

# Set environment variables for optimal performance
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
export NUMEXPR_NUM_THREADS=6
export OPENBLAS_NUM_THREADS=6

echo "⚡ Configured for 6-core parallel processing"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p instagram_data/csv_exports
mkdir -p instagram_data/logs
echo "✅ Data directories created"

# Display system information
echo ""
echo "💻 System Information:"
echo "   OS: $OSTYPE"
echo "   Python: $(python3 --version)"
echo "   CPU Cores: $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 'Unknown')"
echo "   Available RAM: $(free -h 2>/dev/null | grep Mem | awk '{print $2}' || echo 'Unknown')"

echo ""
echo "🎯 Setup completed successfully!"
echo ""
echo "📋 Available commands:"
echo "   1. Run GUI:           python3 gui.py"
echo "   2. Run bot directly:  python3 instagram_bot.py"
echo ""
echo "⚠️  Important notes:"
echo "   - Make sure Chrome browser is installed"
echo "   - Update settings.json with your Instagram credentials"
echo "   - The bot is optimized for 6-core parallel processing"
echo "   - Logs will be saved in instagram_data/logs/"
echo "   - CSV exports will be saved in instagram_data/csv_exports/ (ONE FILE PER BATCH - no more spam!)"
echo ""

echo ""
echo "🧹 Cleaning up old CSV spam files..."
python3 cleanup_old_csvs.py

echo ""
echo "🎉 OPTIMIZATION COMPLETE! Instagram automation is now fully optimized."
echo ""
echo "⚡ PERFORMANCE IMPROVEMENTS APPLIED:"
echo "   ✅ Removed per-follow CSV exports (was creating 50+ files per session)"
echo "   ✅ Now creates ONE batch CSV file per session"
echo "   ✅ Optimized Chrome settings for 6-core processing" 
echo "   ✅ Cleaned up old duplicate CSV files"
echo "   ✅ Added parallel processing support"
echo ""
echo "🚀 USAGE:"
echo "   GUI:           python3 gui.py"
echo "   Fast Unfollow: python3 fast_unfollow_bot.py --workers 6 --csv file.csv --username USER --password PASS"
echo ""

# Ask user what they want to do
read -p "🚀 Do you want to start the optimized GUI now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🖥️ Starting optimized Instagram Bot GUI..."
    python3 gui.py
else
    echo "✅ Setup complete. Run 'python3 gui.py' when ready to use the optimized bot."
fi 