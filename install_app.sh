#!/bin/bash
APP_NAME="Instagram Bot.app"
APPLICATIONS="/Applications"

echo "📱 Installing Instagram Bot..."

if [ ! -d "/Users/diegoaguirre/instagram automation/$APP_NAME" ]; then
    echo "❌ App not found"
    exit 1
fi

if cp -R "/Users/diegoaguirre/instagram automation/$APP_NAME" "$APPLICATIONS/" 2>/dev/null; then
    echo "✅ Installed to Applications"
else
    sudo cp -R "/Users/diegoaguirre/instagram automation/$APP_NAME" "$APPLICATIONS/"
    sudo chmod -R 755 "$APPLICATIONS/$APP_NAME"
    echo "✅ Installed to Applications (with admin permission)"
fi

echo ""
echo "🎉 Installation Complete!"
echo "Find 'Instagram Bot' in Applications folder"

read -p "Launch now? (y/n): " launch
if [[ $launch =~ ^[Yy]$ ]]; then
    open "$APPLICATIONS/$APP_NAME"
fi
