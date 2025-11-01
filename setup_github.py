#!/usr/bin/env python3
"""
GitHub Repository Setup Script
Initializes Git, creates commits, and prepares for GitHub push
"""
import subprocess
import sys
import os
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_color(message, color):
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")

def run_command(command, check=True, capture_output=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Command failed: {command}", Colors.RED)
            print_color(f"Error: {e.stderr}", Colors.RED)
        return None

def check_git_installed():
    """Check if Git is installed"""
    result = run_command("git --version", check=False)
    if result:
        print_color(f"✅ Git installed: {result}", Colors.GREEN)
        return True
    else:
        print_color("❌ Git is not installed. Please install Git from https://git-scm.com/", Colors.RED)
        return False

def initialize_git():
    """Initialize Git repository"""
    if Path(".git").exists():
        print_color("✅ Git repository already initialized", Colors.GREEN)
        return True
    else:
        print_color("📁 Initializing Git repository...", Colors.YELLOW)
        run_command("git init")
        print_color("✅ Git repository initialized", Colors.GREEN)
        return True

def configure_git():
    """Configure Git user if not already configured"""
    git_user = run_command("git config user.name", check=False)
    git_email = run_command("git config user.email", check=False)
    
    if not git_user:
        print()
        user_name = input("Enter your name for Git commits: ")
        run_command(f'git config user.name "{user_name}"')
    
    if not git_email:
        print()
        user_email = input("Enter your email for Git commits: ")
        run_command(f'git config user.email "{user_email}"')
    
    print()
    print_color("📝 Git configuration:", Colors.CYAN)
    git_user = run_command("git config user.name")
    git_email = run_command("git config user.email")
    print(f"   Name: {git_user}")
    print(f"   Email: {git_email}")

def check_env_file():
    """Check for .env file and ensure it's in .gitignore"""
    print()
    if Path(".env").exists():
        print_color("⚠️  WARNING: .env file exists. Make sure it's in .gitignore!", Colors.YELLOW)
        
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()
        
        if "\n.env\n" in gitignore_content or gitignore_content.startswith(".env\n"):
            print_color("✅ .env is properly excluded in .gitignore", Colors.GREEN)
        else:
            print_color("❌ .env is NOT in .gitignore. Adding it now...", Colors.RED)
            with open(".gitignore", "a") as f:
                f.write("\n.env\n")
    else:
        print_color("ℹ️  No .env file found (will be created later)", Colors.BLUE)

def stage_files():
    """Stage all files for commit"""
    print()
    print_color("📦 Staging files for commit...", Colors.YELLOW)
    run_command("git add .")
    
    print()
    print_color("📊 Git status:", Colors.CYAN)
    status = run_command("git status --short")
    print(status)

def create_initial_commit():
    """Create initial commit"""
    print()
    print_color("💾 Creating initial commit...", Colors.YELLOW)
    
    commit_message = """Initial commit: ATS Kafka Snowflake Streamlit ELT Pipeline

- ATS telemetry simulator with realistic data generation
- Kafka setup with Confluent platform
- Snowflake schema with Dynamic Tables and ELT architecture
- Streamlit dashboard with real-time visualizations
- Docker Compose orchestration
- Comprehensive documentation and setup guides
- Python automation scripts for setup and testing
"""
    
    run_command(f'git commit -m "{commit_message}"')
    print_color("✅ Initial commit created", Colors.GREEN)

def rename_branch():
    """Rename branch to main if needed"""
    current_branch = run_command("git branch --show-current")
    if current_branch != "main":
        print()
        print_color("🔄 Renaming branch to 'main'...", Colors.YELLOW)
        run_command("git branch -M main")

def print_github_instructions():
    """Print instructions for GitHub"""
    print()
    print_color("=" * 80, Colors.CYAN)
    print_color("🎉 Git repository is ready!", Colors.GREEN)
    print_color("=" * 80, Colors.CYAN)
    print()
    print_color("Next steps to push to GitHub:", Colors.YELLOW)
    print()
    print_color("1. Create a new repository on GitHub:", Colors.WHITE)
    print_color("   → Go to https://github.com/new", Colors.GRAY)
    print_color("   → Repository name: ats-kafka-snowflake-streamlit", Colors.GRAY)
    print_color("   → Description: Real-time ATS telemetry pipeline with Kafka, Snowflake, and Streamlit", Colors.GRAY)
    print_color("   → Make it Public (for portfolio)", Colors.GRAY)
    print_color("   → Do NOT initialize with README (we already have one)", Colors.GRAY)
    print()
    print_color("2. Run these commands (replace YOUR_USERNAME):", Colors.WHITE)
    print()
    print_color("   git remote add origin https://github.com/YOUR_USERNAME/ats-kafka-snowflake-streamlit.git", Colors.CYAN)
    print_color("   git push -u origin main", Colors.CYAN)
    print()
    print_color("3. Alternative - if you have GitHub CLI installed:", Colors.WHITE)
    print()
    print_color("   gh repo create ats-kafka-snowflake-streamlit --public --source=. --remote=origin --push", Colors.CYAN)
    print()
    print_color("=" * 80, Colors.CYAN)
    print()

def check_github_cli():
    """Check if GitHub CLI is available and offer to create repo"""
    gh_version = run_command("gh --version", check=False)
    if gh_version:
        print_color("✅ GitHub CLI is installed. You can use the 'gh repo create' command above.", Colors.GREEN)
        print()
        use_gh = input("Would you like to create the GitHub repo now using GitHub CLI? (y/n): ")
        
        if use_gh.lower() in ['y', 'yes']:
            print()
            print_color("🚀 Creating GitHub repository...", Colors.YELLOW)
            
            result = run_command(
                'gh repo create ats-kafka-snowflake-streamlit '
                '--public '
                '--description "Real-time ATS telemetry pipeline: Kafka → Snowflake → Streamlit. ELT architecture with Dynamic Tables." '
                '--source=. '
                '--remote=origin '
                '--push',
                check=False
            )
            
            if result is not None:
                print()
                print_color("🎉 Repository created and pushed to GitHub!", Colors.GREEN)
                print()
                repo_url = run_command("gh repo view --json url --jq .url")
                print_color(f"📍 Repository URL: {repo_url}", Colors.CYAN)
                print()
                print_color("Next steps:", Colors.YELLOW)
                print_color("1. ✅ Update README.md with your GitHub username", Colors.WHITE)
                print_color("2. ✅ Add screenshots of the dashboard", Colors.WHITE)
                print_color("3. ✅ Set up Snowflake and test the pipeline", Colors.WHITE)
                print_color("4. ✅ Share your portfolio project!", Colors.WHITE)
    else:
        print_color("ℹ️  GitHub CLI not installed. Follow manual steps above.", Colors.BLUE)

def print_additional_resources():
    """Print additional resources"""
    print()
    print_color("📚 Additional resources:", Colors.YELLOW)
    print_color("   • README.md - Complete project documentation", Colors.WHITE)
    print_color("   • QUICKSTART_WINDOWS.md - Windows-specific setup guide", Colors.WHITE)
    print_color("   • SNOWFLAKE_SETUP.md - Snowflake configuration guide", Colors.WHITE)
    print()
    print_color("✨ Happy coding!", Colors.GREEN)

def main():
    """Main function"""
    print_color("🚀 Setting up Git repository for ATS Kafka Snowflake Streamlit project", Colors.CYAN)
    print()
    
    # Check if Git is installed
    if not check_git_installed():
        sys.exit(1)
    
    # Initialize Git repository
    if not initialize_git():
        sys.exit(1)
    
    # Configure Git user
    configure_git()
    
    # Check for .env file
    check_env_file()
    
    # Stage all files
    stage_files()
    
    # Create initial commit
    create_initial_commit()
    
    # Rename branch to main
    rename_branch()
    
    # Print GitHub instructions
    print_github_instructions()
    
    # Check GitHub CLI
    check_github_cli()
    
    # Print additional resources
    print_additional_resources()

if __name__ == "__main__":
    main()
