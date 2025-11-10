#!/usr/bin/env python3
"""
Unified Command Line Interface for GenX Trading Platform
"""

import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
import shutil

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich.columns import Columns

from core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Main Typer App ---
app = typer.Typer(
    help="🚀 GenX Trading Platform - Unified CLI",
    rich_markup_mode="rich",
    pretty_exceptions_enable=False
)
console = Console()

# --- AMP Sub-App ---
amp_app = typer.Typer(help="🤖 Automated Model Pipeline - AI trading models and authentication")
app.add_typer(amp_app, name="amp")

# --- GenX Sub-App ---
genx_app = typer.Typer(help="⚙️ GenX FX - Complete trading system management")
app.add_typer(genx_app, name="genx")


# --- Helper Classes (from amp_cli.py and genx_cli.py) ---

class AMPCLI:
    def __init__(self):
        self.project_root = Path.cwd()
        self.plugins_dir = self.project_root / "amp-plugins"
        self.env_file = self.project_root / ".env"
        
    def verify(self, check_dependencies: bool = False, check_env_vars: bool = False,
               check_services: bool = False, check_api_keys: bool = False):
        """Verify installation"""
        with console.status("[bold blue]Verifying installation..."):
            if check_dependencies:
                self._check_dependencies(config.get("amp.dependencies", []))

            if check_env_vars:
                # This check is now informational as env vars are loaded globally
                console.print("NOTE: Environment variables are loaded from .env file.")

            if check_services:
                self._check_services(config.get("amp.enabled_services", []))

            if check_api_keys:
                self._check_api_keys()
        
        console.print("✅ [bold green]Installation verification complete!")

    def test(self, all_tests: bool = False):
        """Run tests"""
        if all_tests:
            with console.status("[bold blue]Running all tests..."):
                self._run_python_tests()
                self._run_node_tests()
        else:
            with console.status("[bold blue]Running specific tests..."):
                self._run_python_tests()

    def deploy(self):
        """Deploy to production"""
        with console.status("[bold blue]Deploying to production..."):
            self._run_docker_deploy()

    def _load_env_vars(self, env_file: str):
        """Load environment variables from file"""
        if Path(env_file).exists():
            console.print(f"📄 [blue]Loading environment variables from {env_file}")

    def _check_dependencies(self, dependencies: List[str]):
        """Check if dependencies are installed"""
        console.print("📦 [blue]Checking dependencies...")
        table = Table(title="Dependencies Status")
        table.add_column("Package", style="cyan")
        table.add_column("Status", style="green")
        
        for dep in dependencies:
            try:
                if ">=" in dep:
                    package = dep.split(">=")[0]
                else:
                    package = dep
                __import__(package.replace("-", "_"))
                table.add_row(package, "✅ Installed")
            except ImportError:
                table.add_row(package, "❌ Not installed")
        
        console.print(table)

    def _check_env_vars(self, env_vars: Dict[str, str]):
        """Check environment variables"""
        console.print("🔑 [blue]Checking environment variables...")
        table = Table(title="Environment Variables Status")
        table.add_column("Variable", style="cyan")
        table.add_column("Status", style="green")
        
        for key, value in env_vars.items():
            if os.getenv(key):
                table.add_row(key, "✅ Set")
            else:
                table.add_row(key, "❌ Not set")
        
        console.print(table)

    def _check_services(self, services: List[str]):
        """Check services"""
        console.print("🔧 [blue]Checking services...")
        table = Table(title="Services Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        
        for service in services:
            service_file = self.project_root / "api" / "services" / f"{service}.py"
            if service_file.exists():
                table.add_row(service, "✅ Available")
            else:
                table.add_row(service, "❌ Not found")
        
        console.print(table)

    def _check_api_keys(self):
        """Check API keys"""
        console.print("🔑 [blue]Checking API keys...")
        table = Table(title="API Keys Status")
        table.add_column("API Key", style="cyan")
        table.add_column("Status", style="green")
        
        required_keys = [
            "GEMINI_API_KEY",
            "BYBIT_API_KEY",
            "BYBIT_API_SECRET"
        ]
        
        for key in required_keys:
            if os.getenv(key):
                table.add_row(key, "✅ Set")
            else:
                table.add_row(key, "❌ Not set")

        console.print(table)

    def _run_python_tests(self):
        """Run Python tests"""
        try:
            import subprocess
            subprocess.run([sys.executable, "run_tests.py"], check=True)
            console.print("✅ [bold green]Python tests passed!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Python tests failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]run_tests.py not found")

    def _run_node_tests(self):
        """Run Node.js tests"""
        try:
            import subprocess
            subprocess.run(["npm", "test"], check=True)
            console.print("✅ [bold green]Node.js tests passed!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Node.js tests failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]npm not found")

    def _run_docker_deploy(self):
        """Run Docker deployment"""
        try:
            import subprocess
            subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", "up", "-d"], check=True)
            console.print("✅ [bold green]Docker deployment successful!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Docker deployment failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]docker-compose not found")

    def show_status(self):
        """Show current AMP status"""
        # Create status panel
        status_text = f"""
[bold cyan]API Provider:[/bold cyan] {config.get('amp.api_provider', 'Not set')}
[bold cyan]Plugins Installed:[/bold cyan] {len(config.get('amp.plugins', []))}
[bold cyan]Services Enabled:[/bold cyan] {len(config.get('amp.enabled_services', []))}
        """

        console.print(Panel(status_text, title="[bold blue]AMP Status Report", border_style="blue"))

        # Plugins table
        plugins = config.get('amp.plugins', [])
        if plugins:
            table = Table(title="Installed Plugins")
            table.add_column("Plugin", style="cyan")
            table.add_column("Source", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Description", style="white")

            for plugin in plugins:
                status = "✅ Enabled" if plugin.get('enabled') else "❌ Disabled"
                table.add_row(
                    plugin.get('name'),
                    plugin.get('source', 'N/A'),
                    status,
                    plugin.get('description', 'No description')
                )

            console.print(table)

        # Services table
        enabled_services = config.get('amp.enabled_services', [])
        if enabled_services:
            table = Table(title="Enabled Services")
            table.add_column("Service", style="cyan")

            for service in enabled_services:
                table.add_row(service)

            console.print(table)

        # Features table
        features = [
            ('Sentiment Analysis', 'features.sentiment_analysis'),
            ('Social Signals', 'features.social_signals'),
            ('News Feeds', 'features.news_feeds'),
            ('WebSocket Streams', 'features.websocket_streams')
        ]

        table = Table(title="Features Status")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")

        for feature_name, feature_key in features:
            status = '✅ Enabled' if config.get(feature_key) else '❌ Disabled'
            table.add_row(feature_name, status)

        console.print(table)

class GenXCLI:
    def __init__(self):
        self.project_root = Path.cwd()
        self.env_file = self.project_root / ".env"
        self.requirements_file = self.project_root / "requirements.txt"
        self.signal_output_dir = self.project_root / "signal_output"

        # Core directories
        self.core_dir = self.project_root / "core"
        self.api_dir = self.project_root / "api"
        self.client_dir = self.project_root / "client"
        self.logs_dir = self.project_root / "logs"

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            'project_root': str(self.project_root),
            'directories': {},
            'files': {},
            'environment': {},
            'dependencies': {},
            'services': {},
            'forexconnect': {}
        }

        # Check directories
        key_dirs = ['core', 'api', 'client', 'signal_output', 'logs', 'config', 'ai_models']
        for dir_name in key_dirs:
            dir_path = self.project_root / dir_name
            status['directories'][dir_name] = {
                'exists': dir_path.exists(),
                'path': str(dir_path),
                'items': len(list(dir_path.iterdir())) if dir_path.exists() else 0
            }
        
        # Check important files
        key_files = ['.env', '.env.example', 'requirements.txt', 'main.py', 'config.yaml', 'package.json']
        for file_name in key_files:
            file_path = self.project_root / file_name
            status['files'][file_name] = {
                'exists': file_path.exists(),
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None
            }

        # Check Python environment
        try:
            import pandas
            status['dependencies']['pandas'] = pandas.__version__
        except ImportError:
            status['dependencies']['pandas'] = None

        try:
            import openpyxl
            status['dependencies']['openpyxl'] = openpyxl.__version__
        except ImportError:
            status['dependencies']['openpyxl'] = None

        try:
            import forexconnect
            status['forexconnect']['available'] = True
            status['forexconnect']['module_path'] = forexconnect.__file__
        except ImportError:
            status['forexconnect']['available'] = False

        # Check ForexConnect environment
        fc_env = self.project_root / "forexconnect_env_37"
        if fc_env.exists():
            status['forexconnect']['env_path'] = str(fc_env)
            status['forexconnect']['env_exists'] = True
        else:
            status['forexconnect']['env_exists'] = False

        return status

# --- Merged and Refactored Commands ---

@app.command()
def overview():
    """Show system overview and status."""
    console.print(Panel.fit(
        "[bold blue]🚀 GenX Trading Platform - Unified CLI[/bold blue]\n"
        "[dim]Unified interface for all trading system components[/dim]",
        border_style="blue"
    ))
    # ... (logic from HeadCLI.show_overview)

@app.command()
def status():
    """Show comprehensive system status."""
    console.print("📊 [bold]System Status Report[/bold]")
    console.print("=" * 50)
    
    console.print("\n🤖 [blue]AMP Status:[/blue]")
    amp_status()
    
    console.print("\n⚙️ [green]GenX Status:[/green]")
    genx_status()

# --- AMP Commands ---

@amp_app.command("status")
def amp_status():
    """Show current AMP status"""
    amp = AMPCLI()
    amp.show_status()

@amp_app.command("verify")
def amp_verify(
    check_dependencies: bool = typer.Option(False, "--check-dependencies", help="Check dependencies"),
    check_env_vars: bool = typer.Option(False, "--check-env-vars", help="Check environment variables"),
    check_services: bool = typer.Option(False, "--check-services", help="Check services"),
    check_api_keys: bool = typer.Option(False, "--check-api-keys", help="Check API keys")
):
    """Verify AMP installation"""
    amp = AMPCLI()
    amp.verify(check_dependencies, check_env_vars, check_services, check_api_keys)

@amp_app.command("test")
def amp_test(
    all_tests: bool = typer.Option(False, "--all", help="Run all tests")
):
    """Run tests"""
    amp = AMPCLI()
    amp.test(all_tests)

@amp_app.command("deploy")
def amp_deploy():
    """Deploy to production"""
    amp = AMPCLI()
    amp.deploy()

@amp_app.command("run")
def amp_run():
    """Run the next job"""
    console.print("🚀 [bold blue]AMP Job Runner - Starting Next Job")
    console.print("=" * 50)

    # Import and run the job runner
    try:
        from amp_job_runner import AMPJobRunner
        runner = AMPJobRunner()
        asyncio.run(runner.run_next_job())
    except ImportError:
        console.print("❌ [bold red]AMP Job Runner not found. Please ensure amp_job_runner.py exists.")

@amp_app.command("auth")
def amp_auth(
    token: Optional[str] = typer.Option(None, "--token", help="Authentication token"),
    logout: bool = typer.Option(False, "--logout", help="Logout current user"),
    status: bool = typer.Option(False, "--status", help="Show authentication status")
):
    """Manage authentication"""
    try:
        from amp_auth import authenticate_user, check_auth, logout_user, get_user_info

        if logout:
            logout_user()
        elif status:
            if check_auth():
                user_info = get_user_info()
                console.print(f"✅ [bold green]Authenticated as: {user_info['user_id']}")
            else:
                console.print("❌ [bold red]Not authenticated")
        elif token:
            if authenticate_user(token):
                console.print("✅ [bold green]Authentication successful!")
            else:
                console.print("❌ [bold red]Authentication failed!")
        else:
            console.print("Please provide a token with --token or use --status to check current auth")

    except ImportError:
        console.print("❌ [bold red]Authentication module not found")

@amp_app.command("schedule")
def amp_schedule(
    start: bool = typer.Option(False, "--start", help="Start the scheduler"),
    stop: bool = typer.Option(False, "--stop", help="Stop the scheduler"),
    status: bool = typer.Option(False, "--status", help="Show scheduler status"),
    interval: Optional[int] = typer.Option(None, "--interval", help="Set job interval in minutes"),
    enable: bool = typer.Option(False, "--enable", help="Enable scheduler"),
    disable: bool = typer.Option(False, "--disable", help="Disable scheduler")
):
    """Manage automated job scheduling"""
    try:
        from amp_scheduler import start_scheduler, stop_scheduler, get_scheduler_status, update_scheduler_config

        if start:
            console.print("🚀 [bold blue]Starting AMP Scheduler...")
            start_scheduler()
        elif stop:
            console.print("⏹️ [bold yellow]Stopping AMP Scheduler...")
            stop_scheduler()
        elif status:
            status_info = get_scheduler_status()
            console.print(f"📊 [bold blue]Scheduler Status:")
            console.print(f"   Running: {'✅' if status_info['is_running'] else '❌'}")
            console.print(f"   Enabled: {'✅' if status_info['config']['enabled'] else '❌'}")
            console.print(f"   Interval: {status_info['config']['interval_minutes']} minutes")
            if status_info['last_run']:
                console.print(f"   Last Run: {status_info['last_run']}")
        elif interval:
            update_scheduler_config(interval_minutes=interval)
            console.print(f"✅ [bold green]Scheduler interval updated to {interval} minutes")
        elif enable:
            update_scheduler_config(enabled=True)
            console.print("✅ [bold green]Scheduler enabled")
        elif disable:
            update_scheduler_config(enabled=False)
            console.print("❌ [bold red]Scheduler disabled")
        else:
            console.print("Please specify an action: --start, --stop, --status, --interval, --enable, or --disable")

    except ImportError:
        console.print("❌ [bold red]Scheduler module not found")

@amp_app.command("monitor")
def amp_monitor(
    dashboard: bool = typer.Option(False, "--dashboard", help="Show real-time dashboard"),
    status: bool = typer.Option(False, "--status", help="Show system status"),
    report: bool = typer.Option(False, "--report", help="Generate monitoring report"),
    alerts: bool = typer.Option(False, "--alerts", help="Show active alerts")
):
    """Monitor system performance and status"""
    try:
        from amp_monitor import get_system_status, generate_report, display_dashboard

        if dashboard:
            console.print("📊 [bold blue]Starting AMP Monitoring Dashboard...")
            display_dashboard()
        elif status:
            status_info = get_system_status()
            console.print(f"📊 [bold blue]System Status:")

            # Authentication
            auth = status_info["authentication"]
            console.print(f"   🔐 Auth: {'✅' if auth['status'] == 'authenticated' else '❌'}")
            if auth.get("user_id"):
                console.print(f"   👤 User: {auth['user_id']}")

            # Scheduler
            scheduler = status_info["scheduler"]
            console.print(f"   ⏰ Scheduler: {'✅' if scheduler.get('is_running') else '❌'}")

            # Jobs
            jobs = status_info["jobs"]
            console.print(f"   📊 Jobs: {jobs.get('total_jobs', 0)} (Success: {jobs.get('success_rate', 0.0):.1f}%)")

            # Performance
            perf = status_info["performance"]
            uptime_hours = perf.get('uptime_seconds', 0) / 3600
            console.print(f"   ⚡ Uptime: {uptime_hours:.1f}h, Logs: {perf.get('logs_size_mb', 0)}MB")

            # Alerts
            alerts_list = status_info["alerts"]
            if alerts_list:
                console.print(f"   🚨 Alerts: {len(alerts_list)} active")
            else:
                console.print(f"   ✅ No alerts")

        elif report:
            report_file = generate_report()
            if report_file:
                console.print(f"✅ [bold green]Report generated: {report_file}")
            else:
                console.print("❌ [bold red]Failed to generate report")
        elif alerts:
            status_info = get_system_status()
            alerts_list = status_info["alerts"]
            if alerts_list:
                console.print(f"🚨 [bold red]Active Alerts:")
                for alert in alerts_list:
                    level_icon = "🔴" if alert["level"] == "critical" else "🟡" if alert["level"] == "warning" else "🔵"
                    console.print(f"   {level_icon} {alert['message']}")
            else:
                console.print("✅ [bold green]No active alerts")
        else:
            console.print("Please specify an action: --dashboard, --status, --report, or --alerts")

    except ImportError:
        console.print("❌ [bold red]Monitor module not found")


# --- GenX Commands ---

@genx_app.command("status")
def genx_status():
    """Show comprehensive GenX system status"""
    cli = GenXCLI()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing system status...", total=1)
        status_info = cli.get_system_status()
        progress.update(task, completed=1)

    # Display system overview
    console.print(Panel.fit(
        "[bold green]GenX FX Trading System Status[/bold green]",
        subtitle=f"Project Root: {status_info['project_root']}"
    ))

    # Directories table
    dir_table = Table(title="📁 Project Directories")
    dir_table.add_column("Directory", style="cyan")
    dir_table.add_column("Status", style="green")
    dir_table.add_column("Items", justify="right")
    dir_table.add_column("Path", style="dim")

    for name, info in status_info['directories'].items():
        status_icon = "✅" if info['exists'] else "❌"
        dir_table.add_row(
            name,
            f"{status_icon} {'Exists' if info['exists'] else 'Missing'}",
            str(info['items']) if info['exists'] else "N/A",
            info['path']
        )

    console.print(dir_table)
    console.print()

    # Files table
    file_table = Table(title="📄 Important Files")
    file_table.add_column("File", style="cyan")
    file_table.add_column("Status", style="green")
    file_table.add_column("Size", justify="right")
    file_table.add_column("Last Modified", style="dim")

    for name, info in status_info['files'].items():
        status_icon = "✅" if info['exists'] else "❌"
        size_str = f"{info['size']:,} bytes" if info['exists'] else "N/A"
        modified_str = info['modified'][:19] if info['modified'] else "N/A"

        file_table.add_row(
            name,
            f"{status_icon} {'Exists' if info['exists'] else 'Missing'}",
            size_str,
            modified_str
        )

    console.print(file_table)
    console.print()

    # Dependencies and ForexConnect
    deps_table = Table(title="🔧 Dependencies & ForexConnect")
    deps_table.add_column("Component", style="cyan")
    deps_table.add_column("Status", style="green")
    deps_table.add_column("Version/Details", style="dim")

    # Python dependencies
    for dep, version in status_info['dependencies'].items():
        status_icon = "✅" if version else "❌"
        version_str = version if version else "Not installed"
        deps_table.add_row(dep, f"{status_icon}", version_str)

    # ForexConnect
    fc_info = status_info['forexconnect']
    fc_status = "✅ Available" if fc_info['available'] else "❌ Not available"
    fc_details = fc_info.get('module_path', 'Not found')
    deps_table.add_row("ForexConnect", fc_status, fc_details)

    if fc_info['env_exists']:
        deps_table.add_row("FC Environment", "✅ Found", fc_info['env_path'])
    else:
        deps_table.add_row("FC Environment", "❌ Missing", "forexconnect_env_37/")

    console.print(deps_table)

@genx_app.command("init")
def genx_init():
    """Initialize or setup the GenX FX system"""
    cli = GenXCLI()

    console.print(Panel.fit(
        "[bold green]GenX FX System Initialization[/bold green]",
        subtitle="Setting up your trading system"
    ))
    
    # Create essential directories
    essential_dirs = ['signal_output', 'logs', 'config', 'ai_models', 'data']

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Creating directories...", total=len(essential_dirs))

        for dir_name in essential_dirs:
            dir_path = cli.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                console.print(f"  ✅ Created: {dir_name}/")
            else:
                console.print(f"  ✅ Exists: {dir_name}/")
            progress.advance(task)

    # Create .env file if it doesn't exist
    if not cli.env_file.exists():
        env_example = cli.project_root / ".env.example"
        if env_example.exists():
            shutil.copy2(env_example, cli.env_file)
            console.print("  ✅ Created .env from .env.example")
        else:
            console.print("  ⚠️ No .env.example found to copy")

    console.print("\n[bold green]✅ Initialization complete![/bold green]")
    console.print("Next steps:")
    console.print("  1. Run: [cyan]genx config[/cyan] to configure API keys")
    console.print("  2. Run: [cyan]genx excel demo[/cyan] to test signal generation")
    console.print("  3. Run: [cyan]genx forexconnect test[/cyan] to test FXCM connection")

@genx_app.command("config")
def genx_config():
    """Configure API keys and system settings"""
    cli = GenXCLI()

    console.print(Panel.fit(
        "[bold green]GenX FX Configuration[/bold green]",
        subtitle="Configure API keys and settings"
    ))

    # Show current configuration status
    config_table = Table(title="🔧 Configuration Status")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Status", style="green")
    config_table.add_column("Current Value", style="dim")

    # Check important environment variables
    important_vars = [
        'FXCM_USERNAME', 'FXCM_PASSWORD', 'FXCM_CONNECTION_TYPE',
        'GEMINI_API_KEY', 'TRADING_ENABLED', 'RISK_PERCENTAGE'
    ]

    for var in important_vars:
        current_value = config.get_env(var, 'Not set')
        is_set = current_value != 'Not set'
        status_icon = "✅" if is_set else "❌"

        # Mask sensitive values
        display_value = current_value
        if 'PASSWORD' in var or 'KEY' in var or 'SECRET' in var:
            if is_set and current_value != 'Not set':
                display_value = f"{current_value[:4]}***{current_value[-4:]}" if len(current_value) > 8 else "***"

        config_table.add_row(var, f"{status_icon}", display_value)

    console.print(config_table)
    console.print()

    if Confirm.ask("Would you like to configure settings now?"):
        # FXCM Configuration
        console.print("\n[bold yellow]📊 FXCM ForexConnect Configuration[/bold yellow]")

        current_username = config.get_env('FXCM_USERNAME', '')
        username = Prompt.ask("FXCM Username", default=current_username)

        password = Prompt.ask("FXCM Password", password=True)

        connection_type = Prompt.ask(
            "Connection Type",
            choices=["Demo", "Real"],
            default=config.get_env('FXCM_CONNECTION_TYPE', 'Demo')
        )

        # Trading Configuration
        console.print("\n[bold yellow]⚖️ Risk Management Configuration[/bold yellow]")

        trading_enabled = Confirm.ask("Enable live trading?", default=config.get_env('TRADING_ENABLED', 'false').lower() == 'true')
        risk_percentage = Prompt.ask(
            "Risk percentage per trade",
            default=config.get_env('RISK_PERCENTAGE', '2.0')
        )

        # Write to .env file
        env_content = []
        if cli.env_file.exists():
            with open(cli.env_file, 'r') as f:
                env_content = f.readlines()

        # Update or add variables
        updated_vars = {
            'FXCM_USERNAME': username,
            'FXCM_PASSWORD': password,
            'FXCM_CONNECTION_TYPE': connection_type,
            'TRADING_ENABLED': str(trading_enabled).lower(),
            'RISK_PERCENTAGE': risk_percentage
        }

        # Simple .env update (you might want to use a proper .env library)
        with open(cli.env_file, 'w') as f:
            f.write("# GenX FX Trading System Configuration\n")
            f.write(f"# Updated: {datetime.now().isoformat()}\n\n")

            for key, value in updated_vars.items():
                f.write(f"{key}={value}\n")

            f.write("\n# Add other configuration from .env.example as needed\n")

        console.print("\n[bold green]✅ Configuration saved to .env[/bold green]")

# Excel command group
excel_app = typer.Typer(help="Excel signal generation and management")
genx_app.add_typer(excel_app, name="excel")

@excel_app.command("demo")
def excel_demo(count: int = typer.Option(10, help="Number of signals to generate")):
    """Generate demo Excel signals"""
    console.print(f"[bold green]📊 Generating {count} demo Excel signals...[/bold green]")

    try:
        # Run the demo generator
        import subprocess
        result = subprocess.run([
            sys.executable, "demo_excel_generator.py"
        ], capture_output=True, text=True, cwd=str(Path.cwd()))
        
        if result.returncode == 0:
            console.print("[bold green]✅ Excel demo completed successfully![/bold green]")
            console.print(result.stdout)
        else:
            console.print("[bold red]❌ Excel demo failed![/bold red]")
            console.print(result.stderr)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")

@excel_app.command("live")
def excel_live(count: int = typer.Option(10, help="Number of signals to generate")):
    """Generate Excel signals with live ForexConnect data"""
    console.print(f"[bold green]📊 Generating {count} live Excel signals...[/bold green]")

    try:
        # Run the live generator
        result = subprocess.run([
            sys.executable, "excel_forexconnect_integration.py"
        ], capture_output=True, text=True, cwd=str(Path.cwd()))

        if result.returncode == 0:
            console.print("[bold green]✅ Live Excel generation completed![/bold green]")
            console.print(result.stdout)
        else:
            console.print("[bold red]❌ Live Excel generation failed![/bold red]")
            console.print(result.stderr)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")

@excel_app.command("view")
def excel_view():
    """View generated Excel files"""
    cli = GenXCLI()

    excel_files = list(cli.signal_output_dir.glob("*.xlsx"))

    if not excel_files:
        console.print("[yellow]No Excel files found in signal_output/[/yellow]")
        return

    table = Table(title="📊 Generated Excel Files")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", style="dim")
    table.add_column("Action", style="green")

    for file_path in excel_files:
        size = file_path.stat().st_size
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        table.add_row(
            file_path.name,
            f"{size:,} bytes",
            modified.strftime("%Y-%m-%d %H:%M"),
            "Ready to open"
        )

    console.print(table)
    console.print(f"\n📂 Files location: {cli.signal_output_dir}")

# ForexConnect command group
forexconnect_app = typer.Typer(help="ForexConnect API management")
genx_app.add_typer(forexconnect_app, name="forexconnect")

@forexconnect_app.command("test")
def forexconnect_test():
    """Test ForexConnect connection"""
    console.print("[bold green]🔌 Testing ForexConnect connection...[/bold green]")

    try:
        # Test ForexConnect availability
        result = subprocess.run([
            sys.executable, "-c", "import forexconnect; print('ForexConnect module available')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("✅ ForexConnect module: Available")

            # Test actual connection
            result = subprocess.run([
                sys.executable, "test_forexconnect.py"
            ], capture_output=True, text=True, cwd=str(Path.cwd()))

            console.print("📊 Connection test output:")
            console.print(result.stdout)

            if result.stderr:
                console.print("[yellow]Warnings/Errors:[/yellow]")
                console.print(result.stderr)

        else:
            console.print("❌ ForexConnect module: Not available")
            console.print("💡 Try running: source forexconnect_env_37/bin/activate")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")

@forexconnect_app.command("status")
def forexconnect_status():
    """Show ForexConnect installation status"""
    cli = GenXCLI()

    console.print("[bold green]📊 ForexConnect Status[/bold green]")

    # Check ForexConnect environment
    fc_env = cli.project_root / "forexconnect_env_37"

    table = Table(title="ForexConnect Installation")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")
    
    if fc_env.exists():
        table.add_row("Environment", "✅ Found", str(fc_env))

        # Check if module is available
        fc_python = fc_env / "bin" / "python"
        if fc_python.exists():
            table.add_row("Python Binary", "✅ Available", str(fc_python))

        # Check ForexConnect module
        try:
            result = subprocess.run([
                str(fc_python), "-c", "import forexconnect; print(forexconnect.__file__)"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                table.add_row("ForexConnect Module", "✅ Available", result.stdout.strip())
            else:
                table.add_row("ForexConnect Module", "❌ Error", result.stderr.strip())

        except Exception as e:
            table.add_row("ForexConnect Module", "❌ Error", str(e))
    else:
        table.add_row("Environment", "❌ Missing", "forexconnect_env_37/ not found")

    console.print(table)

@genx_app.command()
def logs():
    """View system logs"""
    cli = GenXCLI()

    log_files = list(cli.logs_dir.glob("*.log")) if cli.logs_dir.exists() else []

    if not log_files:
        console.print("[yellow]No log files found in logs/[/yellow]")
        return

    table = Table(title="📋 System Logs")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", style="dim")

    for log_file in log_files:
        size = log_file.stat().st_size
        modified = datetime.fromtimestamp(log_file.stat().st_mtime)

        table.add_row(
            log_file.name,
            f"{size:,} bytes",
            modified.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

    if log_files and Confirm.ask("View latest log file?"):
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

        console.print(f"\n[bold]📄 {latest_log.name}[/bold] (last 20 lines):")
        console.print(Panel(
            "\n".join(latest_log.read_text().split('\n')[-20:]),
            title=latest_log.name,
            border_style="dim"
        ))

@genx_app.command("inspect-logs")
def inspect_logs(
    workflow_run_id: Optional[str] = typer.Option(None, "--workflow-run-id", help="The ID of the GitHub Actions workflow run.")
):
    """Inspect the logs from the last CI/CD build and deployment."""
    console.print("🔍 [bold blue]Inspecting CI/CD logs...[/bold blue]")

    # GitLab CI/CD command
    console.print("\n[bold]GitLab CI/CD[/bold]")
    try:
        result = subprocess.run(["gitlab-runner", "job", "view", "--last-run", "--log"], capture_output=True, text=True)

        if result.returncode == 0:
            console.print("[green]✅ Last GitLab job log:[/green]")
            console.print(Panel(result.stdout, title="GitLab Log", border_style="green"))
        else:
            console.print("[red]❌ Error fetching GitLab job log:[/red]")
            console.print(Panel(result.stderr, title="GitLab Error", border_style="red"))

    except FileNotFoundError:
        console.print("[yellow]⚠️ gitlab-runner command not found. Is it installed and in your PATH?[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ An error occurred: {e}[/red]")

    # GitHub Actions command
    console.print("\n[bold]GitHub Actions[/bold]")
    if workflow_run_id:
        try:
            result = subprocess.run(["gh", "run", "view", workflow_run_id, "--log"], capture_output=True, text=True)

            if result.returncode == 0:
                console.print(f"[green]✅ GitHub Actions log for run {workflow_run_id}:[/green]")
                console.print(Panel(result.stdout, title="GitHub Actions Log", border_style="green"))
            else:
                console.print(f"[red]❌ Error fetching GitHub Actions log for run {workflow_run_id}:[/red]")
                console.print(Panel(result.stderr, title="GitHub Actions Error", border_style="red"))

        except FileNotFoundError:
            console.print("[yellow]⚠️ gh command not found. Is it installed and in your PATH?[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ An error occurred: {e}[/red]")
    else:
        console.print("[yellow]⚠️ --workflow-run-id not provided. Skipping GitHub Actions log inspection.[/yellow]")
        console.print("💡 To inspect a GitHub Actions log, provide the workflow run ID, e.g.:")
        console.print("   [cyan]genx inspect-logs --workflow-run-id 123456789[/cyan]")

@genx_app.command()
def tree():
    """Show project structure tree"""
    cli = GenXCLI()

    console.print("[bold green]🌳 GenX FX Project Structure[/bold green]")

    tree = Tree("GenX_FX/")

    # Add main directories
    for item in sorted(cli.project_root.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            branch = tree.add(f"📁 {item.name}/")

            # Add some key files in each directory
            try:
                for subitem in sorted(list(item.iterdir())[:5]):  # Limit to first 5 items
                    if subitem.is_file():
                        branch.add(f"📄 {subitem.name}")
                    elif subitem.is_dir():
                        branch.add(f"📁 {subitem.name}/")

                if len(list(item.iterdir())) > 5:
                    branch.add("...")

            except PermissionError:
                branch.add("❌ Permission denied")

    # Add important root files
    important_files = ['.env', '.env.example', 'requirements.txt', 'main.py', 'README.md']
    for file_name in important_files:
        file_path = cli.project_root / file_name
        if file_path.exists():
            tree.add(f"📄 {file_name}")

    console.print(tree)

# --- Chat Command ---

@app.command()
def chat():
    """Start interactive chat with AMP trading system."""
    console.print("💬 [cyan]Starting AMP Chat...[/cyan]")
    try:
        subprocess.run(['python3', 'simple_amp_chat.py'])
    except FileNotFoundError:
        console.print("[red]❌ Error: simple_amp_chat.py not found.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error running chat: {e}[/red]")

@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version")
):
    """
    🚀 GenX Trading Platform - Head CLI
    
    Unified command-line interface that wraps all trading system components:
    • AMP (Automated Model Pipeline) - AI models and authentication
    • GenX FX - Trading system management and ForexConnect
    • Chat - Interactive communication with AMP
    
    Examples:
      head_cli overview              # Show system overview
      head_cli amp auth --status     # Check AMP authentication  
      head_cli genx status           # GenX system status
      head_cli chat                  # Start interactive chat
      head_cli status                # Complete system status
    """
    if version:
        console.print("GenX Trading Platform Head CLI v1.0.0")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        # Show overview if no command provided
        head_cli.show_overview()

if __name__ == "__main__":
    app()