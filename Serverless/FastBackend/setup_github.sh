#!/bin/bash
# 🐙 GitHub Setup Script for FastBackend
# Automatically updates GitHub URLs in all files

set -e

echo "🐙 FastBackend GitHub Setup"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "handler_fast.py" ]; then
    echo "❌ Error: Run this script from Serverless/FastBackend directory"
    exit 1
fi

# Get GitHub configuration
if [ -z "$GITHUB_USERNAME" ]; then
    read -p "🔤 Enter your GitHub username: " GITHUB_USERNAME
fi

if [ -z "$GITHUB_REPO" ]; then
    read -p "📁 Enter your GitHub repository name: " GITHUB_REPO
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    read -p "🔑 Enter your RunPod API key (optional): " RUNPOD_API_KEY
fi

echo ""
echo "📋 Configuration:"
echo "  GitHub Username: $GITHUB_USERNAME"
echo "  GitHub Repo: $GITHUB_REPO"
echo "  RunPod API Key: ${RUNPOD_API_KEY:0:10}..."

read -p "🤔 Is this correct? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Setup cancelled"
    exit 1
fi

echo ""
echo "🔧 Updating files..."

# Update startup.sh
if [ -f "startup.sh" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" startup.sh
    sed -i.bak "s/YOUR_REPO/$GITHUB_REPO/g" startup.sh
    echo "✅ Updated startup.sh"
    rm -f startup.sh.bak
fi

# Update deploy_fast.py
if [ -f "deploy_fast.py" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" deploy_fast.py
    sed -i.bak "s/YOUR_REPO/$GITHUB_REPO/g" deploy_fast.py
    echo "✅ Updated deploy_fast.py"
    rm -f deploy_fast.py.bak
fi

# Update deploy_with_mcp.py
if [ -f "deploy_with_mcp.py" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" deploy_with_mcp.py
    sed -i.bak "s/YOUR_REPO/$GITHUB_REPO/g" deploy_with_mcp.py
    echo "✅ Updated deploy_with_mcp.py"
    rm -f deploy_with_mcp.py.bak
fi

# Update README.md
if [ -f "README.md" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" README.md
    sed -i.bak "s/YOUR_REPO/$GITHUB_REPO/g" README.md
    echo "✅ Updated README.md"
    rm -f README.md.bak
fi

# Create config.env from template
if [ ! -f "config.env" ] && [ -f "config.env.template" ]; then
    cp config.env.template config.env
    
    # Update config.env with provided values
    if [ -n "$GITHUB_USERNAME" ]; then
        sed -i.bak "s/your_github_username/$GITHUB_USERNAME/g" config.env
    fi
    
    if [ -n "$GITHUB_REPO" ]; then
        sed -i.bak "s/your_repo_name/$GITHUB_REPO/g" config.env
    fi
    
    if [ -n "$RUNPOD_API_KEY" ]; then
        sed -i.bak "s/your_runpod_api_key_here/$RUNPOD_API_KEY/g" config.env
    fi
    
    echo "✅ Created config.env"
    rm -f config.env.bak
fi

# Set environment variables for current session
export GITHUB_USERNAME="$GITHUB_USERNAME"
export GITHUB_REPO="$GITHUB_REPO"
if [ -n "$RUNPOD_API_KEY" ]; then
    export RUNPOD_API_KEY="$RUNPOD_API_KEY"
fi

echo ""
echo "🎉 GitHub setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Commit and push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Setup FastBackend with GitHub integration'"
echo "   git push"
echo ""
echo "2. Deploy to RunPod:"
echo "   python deploy_fast.py"
echo "   # or"
echo "   python deploy_with_mcp.py"
echo ""
echo "3. Test locally first (optional):"
echo "   python test_local.py"
echo ""
echo "🚀 Your FastBackend is ready for deployment!"
echo ""
echo "📋 Environment variables set:"
echo "   export GITHUB_USERNAME='$GITHUB_USERNAME'"
echo "   export GITHUB_REPO='$GITHUB_REPO'"
if [ -n "$RUNPOD_API_KEY" ]; then
    echo "   export RUNPOD_API_KEY='${RUNPOD_API_KEY:0:10}...'"
fi
echo ""
echo "🔗 Your startup URL will be:"
echo "   https://raw.githubusercontent.com/$GITHUB_USERNAME/$GITHUB_REPO/main/Serverless/FastBackend/startup.sh"