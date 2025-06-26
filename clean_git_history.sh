#!/bin/bash
# Git History Cleaning Script
# This will remove all traces of hardcoded credentials from git history

echo "🧹 Git History Cleaning Script"
echo "=============================="
echo ""
echo "⚠️  WARNING: This will rewrite your entire git history!"
echo "⚠️  Make sure you have a backup before proceeding."
echo ""

read -p "Do you want to continue? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "🔍 Checking for git-filter-repo..."

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo not found. Installing..."
    
    # Try different installation methods
    if command -v pip3 &> /dev/null; then
        pip3 install git-filter-repo
    elif command -v pip &> /dev/null; then
        pip install git-filter-repo
    elif command -v brew &> /dev/null; then
        brew install git-filter-repo
    else
        echo "❌ Could not install git-filter-repo automatically."
        echo "Please install it manually:"
        echo "  pip install git-filter-repo"
        echo "  or brew install git-filter-repo"
        exit 1
    fi
fi

echo "✅ git-filter-repo found"
echo ""

echo "🧹 Removing sensitive content from git history..."

# Create filter expressions file
cat > filter-expressions.txt << 'EOF'
# Remove hardcoded passwords
literal:b@seb@ll=REMOVED_PASSWORD
literal:deegz.mp3=REMOVED_USERNAME

# Remove sensitive file contents
literal:"username": "deegz.mp3"=**REMOVED**
literal:"password": "b@seb@ll"=**REMOVED**

# Remove Instagram login patterns
regex:password_input\.send_keys\("[^"]*"\)=password_input.send_keys("**REMOVED**")
regex:username_input\.send_keys\("[^"]*"\)=username_input.send_keys("**REMOVED**")
EOF

# Run git-filter-repo to clean history
echo "🔄 Running git-filter-repo..."
git filter-repo --replace-text filter-expressions.txt --force

if [ $? -eq 0 ]; then
    echo "✅ Git history cleaned successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review the changes: git log --oneline"
    echo "2. Test that everything still works"
    echo "3. Force push to update remote: git push --force-with-lease origin main"
    echo ""
    echo "⚠️  Note: Collaborators will need to re-clone the repository"
else
    echo "❌ Git history cleaning failed"
    exit 1
fi

# Clean up
rm -f filter-expressions.txt

echo ""
echo "🎉 Git history cleaning complete!"
echo "Your repository is now safe to make public." 