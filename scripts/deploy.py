# ============================================
# File: scripts/deploy.py
# ============================================

#!/usr/bin/env python3
"""
Deployment Script
File: scripts/deploy.py
"""

import os
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all requirements are met"""
    print("Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    
    print("✅ Python version OK")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    return True


def deploy_local():
    """Deploy locally"""
    print("\n📦 Deploying locally...")
    
    # Create virtual environment
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Activate and install
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    print("Installing dependencies...")
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"])
    
    # Run setup
    print("Running setup...")
    subprocess.run([sys.executable, "scripts/setup.py"])
    
    print("✅ Local deployment complete!")
    print("\nTo run the app:")
    print("  source venv/bin/activate  # Linux/Mac")
    print("  venv\\Scripts\\activate    # Windows")
    print("  streamlit run app/main.py")


def deploy_docker():
    """Deploy with Docker"""
    print("\n🐳 Deploying with Docker...")
    
    # Build image
    print("Building Docker image...")
    subprocess.run(["docker-compose", "build"])
    
    # Start containers
    print("Starting containers...")
    subprocess.run(["docker-compose", "up", "-d"])
    
    print("✅ Docker deployment complete!")
    print("\nApp running at: http://localhost:8501")
    print("\nUseful commands:")
    print("  docker-compose logs -f     # View logs")
    print("  docker-compose down        # Stop containers")


def deploy_heroku():
    """Deploy to Heroku"""
    print("\n☁️  Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    try:
        subprocess.run(["heroku", "--version"], check=True, capture_output=True)
    except:
        print("❌ Heroku CLI not found. Please install from https://cli.heroku.com")
        return
    
    # Create Procfile
    with open('Procfile', 'w') as f:
        f.write("web: streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0\n")
    
    # Create setup.sh for Heroku
    with open('setup.sh', 'w') as f:
        f.write("""mkdir -p ~/.streamlit/

echo "\\
[general]\\n\\
email = \\"your-email@domain.com\\"\\n\\
" > ~/.streamlit/credentials.toml

echo "\\
[server]\\n\\
headless = true\\n\\
enableCORS=false\\n\\
port = $PORT\\n\\
" > ~/.streamlit/config.toml
""")
    
    # Git operations
    print("Initializing git repository...")
    subprocess.run(["git", "init"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial deployment"])
    
    # Create Heroku app
    print("Creating Heroku app...")
    app_name = input("Enter app name (or press Enter for random): ").strip()
    
    if app_name:
        subprocess.run(["heroku", "create", app_name])
    else:
        subprocess.run(["heroku", "create"])
    
    # Set config vars
    print("Setting config vars...")
    subprocess.run(["heroku", "config:set", f"OPENROUTER_API_KEY={os.getenv('OPENROUTER_API_KEY', '')}"])
    
    # Deploy
    print("Deploying to Heroku...")
    subprocess.run(["git", "push", "heroku", "main"])
    
    print("✅ Heroku deployment complete!")
    print("\nOpen your app:")
    print("  heroku open")


def main():
    """Main deployment function"""
    print("=" * 50)
    print("Multi-Bank Reconciliation System - Deploy")
    print("=" * 50)
    print()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix issues and try again.")
        return
    
    # Choose deployment method
    print("\nSelect deployment method:")
    print("1. Local (Development)")
    print("2. Docker (Production)")
    print("3. Heroku (Cloud)")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        deploy_local()
    elif choice == "2":
        deploy_docker()
    elif choice == "3":
        deploy_heroku()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()


# ============================================
# File: .github/workflows/ci.yml
# ============================================

name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=models --cov=services
    
    - name: Lint
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t deposito-rekon:latest .
    
    - name: Run Docker container
      run: |
        docker run -d -p 8501:8501 deposito-rekon:latest
        sleep 10
        curl --fail http://localhost:8501/_stcore/health || exit 1