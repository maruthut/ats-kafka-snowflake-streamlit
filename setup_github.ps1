#!/usr/bin/env pwsh
# GitHub Repository Setup Script for Windows
# This script initializes Git, creates commits, and prepares for GitHub push

Write-Host "🚀 Setting up Git repository for ATS Kafka Snowflake Streamlit project" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Initialize Git repository if not already initialized
if (-not (Test-Path .git)) {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Configure Git user (if not already configured)
$gitUser = git config user.name
$gitEmail = git config user.email

if ([string]::IsNullOrEmpty($gitUser)) {
    Write-Host ""
    $userName = Read-Host "Enter your name for Git commits"
    git config user.name "$userName"
}

if ([string]::IsNullOrEmpty($gitEmail)) {
    Write-Host ""
    $userEmail = Read-Host "Enter your email for Git commits"
    git config user.email "$userEmail"
}

Write-Host ""
Write-Host "📝 Git configuration:" -ForegroundColor Cyan
Write-Host "   Name: $(git config user.name)"
Write-Host "   Email: $(git config user.email)"

# Check for .env file
Write-Host ""
if (Test-Path .env) {
    Write-Host "⚠️  WARNING: .env file exists. Make sure it's in .gitignore!" -ForegroundColor Yellow
    if (Select-String -Path .gitignore -Pattern "^\.env$" -Quiet) {
        Write-Host "✅ .env is properly excluded in .gitignore" -ForegroundColor Green
    } else {
        Write-Host "❌ .env is NOT in .gitignore. Adding it now..." -ForegroundColor Red
        Add-Content -Path .gitignore -Value ".env"
    }
} else {
    Write-Host "ℹ️  No .env file found (will be created later)" -ForegroundColor Blue
}

# Stage all files
Write-Host ""
Write-Host "📦 Staging files for commit..." -ForegroundColor Yellow
git add .

# Show status
Write-Host ""
Write-Host "📊 Git status:" -ForegroundColor Cyan
git status --short

# Create initial commit
Write-Host ""
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: ATS Kafka Snowflake Streamlit ELT Pipeline

- ATS telemetry simulator with realistic data generation
- Kafka setup with Confluent platform
- Snowflake schema with Dynamic Tables and ELT architecture
- Streamlit dashboard with real-time visualizations
- Docker Compose orchestration
- Comprehensive documentation and setup guides
"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Rename branch to main (if needed)
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host ""
    Write-Host "🔄 Renaming branch to 'main'..." -ForegroundColor Yellow
    git branch -M main
}

# Instructions for GitHub
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎉 Git repository is ready!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps to push to GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor White
Write-Host "   → Go to https://github.com/new" -ForegroundColor Gray
Write-Host "   → Repository name: ats-kafka-snowflake-streamlit" -ForegroundColor Gray
Write-Host "   → Description: Real-time ATS telemetry pipeline with Kafka, Snowflake, and Streamlit" -ForegroundColor Gray
Write-Host "   → Make it Public (for portfolio)" -ForegroundColor Gray
Write-Host "   → Do NOT initialize with README (we already have one)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run these commands (replace YOUR_USERNAME):" -ForegroundColor White
Write-Host ""
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/ats-kafka-snowflake-streamlit.git" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Alternative - if you have GitHub CLI installed:" -ForegroundColor White
Write-Host ""
Write-Host "   gh repo create ats-kafka-snowflake-streamlit --public --source=. --remote=origin --push" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is available
try {
    $ghVersion = gh --version
    Write-Host "✅ GitHub CLI is installed. You can use the 'gh repo create' command above." -ForegroundColor Green
    Write-Host ""
    $useGHCLI = Read-Host "Would you like to create the GitHub repo now using GitHub CLI? (y/n)"
    
    if ($useGHCLI -eq 'y' -or $useGHCLI -eq 'Y') {
        Write-Host ""
        Write-Host "🚀 Creating GitHub repository..." -ForegroundColor Yellow
        gh repo create ats-kafka-snowflake-streamlit `
            --public `
            --description "Real-time ATS telemetry pipeline: Kafka → Snowflake → Streamlit. ELT architecture with Dynamic Tables." `
            --source=. `
            --remote=origin `
            --push
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "🎉 Repository created and pushed to GitHub!" -ForegroundColor Green
            Write-Host ""
            $repoUrl = gh repo view --json url --jq .url
            Write-Host "📍 Repository URL: $repoUrl" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "1. ✅ Update README.md with your GitHub username" -ForegroundColor White
            Write-Host "2. ✅ Add screenshots of the dashboard" -ForegroundColor White
            Write-Host "3. ✅ Set up Snowflake and test the pipeline" -ForegroundColor White
            Write-Host "4. ✅ Share your portfolio project!" -ForegroundColor White
        }
    }
} catch {
    Write-Host "ℹ️  GitHub CLI not installed. Follow manual steps above." -ForegroundColor Blue
}

Write-Host ""
Write-Host "📚 Additional resources:" -ForegroundColor Yellow
Write-Host "   • README.md - Complete project documentation" -ForegroundColor White
Write-Host "   • QUICKSTART_WINDOWS.md - Windows-specific setup guide" -ForegroundColor White
Write-Host "   • SNOWFLAKE_SETUP.md - Snowflake configuration guide" -ForegroundColor White
Write-Host ""
Write-Host "✨ Happy coding!" -ForegroundColor Green
