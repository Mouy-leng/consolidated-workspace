#!/bin/bash
# Gitpod CLI Wrapper for AMP Trading System
# This script provides Gitpod-like functionality for the AMP system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# AMP System configuration
AMP_ENV=${AMP_ENV:-development}
WORKSPACE_ROOT=$(pwd)

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to show help
show_help() {
    cat << EOF
Gitpod CLI Wrapper for AMP Trading System

Usage: ./gp <command> [options]

Commands:
    info          Show workspace information
    status        Show AMP system status
    ports         List and manage ports
    tasks         List and manage tasks
    env           Manage environment variables
    docs          Open documentation
    init          Initialize AMP system
    run           Run AMP CLI commands
    docker        Docker operations
    monitor       Start monitoring dashboard
    help          Show this help message

Examples:
    ./gp info                    # Show workspace info
    ./gp status                  # Show AMP system status
    ./gp ports list              # List open ports
    ./gp run --help              # Show AMP CLI help
    ./gp docker build            # Build Docker image
    ./gp monitor                 # Start monitoring dashboard

EOF
}

# Function to show workspace info
show_info() {
    print_header "Workspace Information"
    echo "Workspace Root: $WORKSPACE_ROOT"
    echo "AMP Environment: $AMP_ENV"
    echo "Python Version: $(python3 --version 2>/dev/null || echo 'Not installed')"
    echo "Docker Version: $(docker --version 2>/dev/null || echo 'Not installed')"
    echo "Git Branch: $(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
    echo "Gitpod Workspace ID: ${GITPOD_WORKSPACE_ID:-'Not in Gitpod'}"
}

# Function to show AMP system status
show_status() {
    print_header "AMP System Status"
    
    # Check if AMP CLI is available
    if [ -f "amp_cli.py" ]; then
        print_status "AMP CLI: Available"
        python3 amp_cli.py --help > /dev/null 2>&1 && print_status "AMP CLI: Working" || print_warning "AMP CLI: Not working"
    else
        print_error "AMP CLI: Not found"
    fi
    
    # Check environment file
    if [ -f ".env" ]; then
        print_status "Environment: Configured"
    else
        print_warning "Environment: Not configured (run './gp init')"
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_status "Docker: Available"
        docker info > /dev/null 2>&1 && print_status "Docker: Running" || print_warning "Docker: Not running"
    else
        print_error "Docker: Not installed"
    fi
    
    # Check ports
    print_header "Port Status"
    netstat -tlnp 2>/dev/null | grep -E ':(8000|3000|5432|6379)' || print_warning "No AMP ports detected"
}

# Function to list ports
list_ports() {
    print_header "Port Information"
    echo "AMP System Ports:"
    echo "  8000 - AMP API"
    echo "  3000 - Grafana Dashboard"
    echo "  5432 - PostgreSQL"
    echo "  6379 - Redis"
    echo ""
    echo "Currently Open Ports:"
    netstat -tlnp 2>/dev/null | grep LISTEN || echo "No open ports detected"
}

# Function to manage tasks
manage_tasks() {
    print_header "Task Management"
    echo "Available AMP Tasks:"
    echo "  1. Setup Environment"
    echo "  2. Install Dependencies"
    echo "  3. Initialize AMP System"
    echo "  4. Start Scheduler"
    echo "  5. Run Monitoring"
    echo "  6. Build Docker Image"
    echo ""
    echo "To run a task, use: ./gp run <task>"
}

# Function to manage environment
manage_env() {
    print_header "Environment Management"
    if [ -f ".env" ]; then
        echo "Current environment variables:"
        grep -v '^#' .env | grep -v '^$' || echo "No environment variables set"
    else
        print_warning "No .env file found"
        echo "Run './gp init' to create one"
    fi
}

# Function to open documentation
open_docs() {
    print_header "Documentation"
    echo "AMP System Documentation:"
    echo "  - README.md: Main documentation"
    echo "  - AMP_CLI_INSTALLATION.md: CLI setup guide"
    echo "  - DOCKER_DEPLOYMENT_SUMMARY.md: Docker deployment"
    echo "  - setup_docker_secrets.md: Docker secrets setup"
    echo ""
    echo "Opening README.md..."
    if command -v code &> /dev/null; then
        code README.md
    else
        cat README.md | head -50
        echo "... (truncated)"
    fi
}

# Function to initialize AMP system
init_amp() {
    print_header "Initializing AMP System"
    
    # Create necessary directories
    mkdir -p logs reports data
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
        print_warning "Please update .env with your API keys"
    fi
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip3 install -r requirements.txt
    fi
    
    if [ -f "requirements-amp.txt" ]; then
        print_status "Installing AMP dependencies..."
        pip3 install -r requirements-amp.txt
    fi
    
    # Make scripts executable
    chmod +x amp_alias.sh amp_wrapper.py 2>/dev/null || true
    
    print_status "AMP system initialized!"
}

# Function to run AMP CLI commands
run_amp() {
    if [ -z "$1" ]; then
        print_error "No command specified"
        echo "Usage: ./gp run <amp-command>"
        echo "Example: ./gp run --help"
        exit 1
    fi
    
    if [ -f "amp_wrapper.py" ]; then
        python3 amp_wrapper.py "$@"
    elif [ -f "amp_cli.py" ]; then
        python3 amp_cli.py "$@"
    else
        print_error "AMP CLI not found"
        exit 1
    fi
}

# Function to handle Docker operations
docker_ops() {
    case "$1" in
        "build")
            print_header "Building Docker Image"
            docker build -f Dockerfile.production -t keamouyleng/genx-fx:latest .
            ;;
        "run")
            print_header "Running Docker Container"
            docker run -d --name amp-system -p 8000:8000 keamouyleng/genx-fx:latest
            ;;
        "compose")
            print_header "Running with Docker Compose"
            docker-compose -f docker-compose.amp.yml up -d
            ;;
        "logs")
            docker logs amp-system
            ;;
        *)
            print_error "Unknown Docker operation: $1"
            echo "Available operations: build, run, compose, logs"
            ;;
    esac
}

# Function to start monitoring
start_monitor() {
    print_header "Starting AMP Monitoring"
    if [ -f "amp_wrapper.py" ]; then
        python3 amp_wrapper.py monitor --dashboard
    else
        print_error "AMP CLI not found"
    fi
}

# Main command handler
case "$1" in
    "info")
        show_info
        ;;
    "status")
        show_status
        ;;
    "ports")
        list_ports
        ;;
    "tasks")
        manage_tasks
        ;;
    "env")
        manage_env
        ;;
    "docs")
        open_docs
        ;;
    "init")
        init_amp
        ;;
    "run")
        shift
        run_amp "$@"
        ;;
    "docker")
        shift
        docker_ops "$@"
        ;;
    "monitor")
        start_monitor
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Run './gp help' for available commands"
        exit 1
        ;;
esac