#!/usr/bin/env python3
"""
Head CLI - Unified Command Line Interface for GenX Trading Platform
Wraps all existing CLI tools into a single, organized interface
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

import typer
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.tree import Tree
from rich.columns import Columns

# Import the new session orchestration module
from core import session_orchestration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Typer app and Rich console
app = typer.Typer(
    help="🚀 GenX Trading Platform - Head CLI",
    rich_markup_mode="rich",
    pretty_exceptions_enable=False
)
console = Console()

# Create a new Typer app for session commands
session_app = typer.Typer(
    help="📱 Session Orchestration Commands",
    rich_markup_mode="rich"
)
app.add_typer(session_app, name="session")


class HeadCLI:
    def __init__(self):
        self.project_root = Path.cwd()
        self.available_clis = {
            'amp': {
                'file': 'amp_cli.py',
                'description': 'Automated Model Pipeline - AI trading models and authentication',
                'commands': ['update', 'plugin-install', 'config-set', 'verify', 'test', 'deploy', 'status', 'auth', 'schedule', 'monitor']
            },
            'genx': {
                'file': 'genx_cli.py',
                'description': 'GenX FX - Complete trading system management',
                'commands': ['status', 'init', 'config', 'logs', 'tree', 'excel', 'forexconnect']
            },
            'chat': {
                'file': 'simple_amp_chat.py',
                'description': 'Interactive chat with AMP trading system',
                'commands': ['interactive']
            }
        }

        # --- Communication Hub Integration ---
        self.comm_api_url = "http://127.0.0.1:8080/communication"
        self.agent_id_file = self.project_root / "agent_id.json"
        self.agent_id = None
        # In a real multi-agent setup, this would be unique per agent instance
        self.agent_email = "lengkundee01@gmail.com"
        self.agent_name = f"Jules - {os.path.basename(os.getcwd())}" # A more dynamic name
        self._register_agent()

        # --- Session Orchestration Config ---
        self.session_config = self.load_session_config()

    def load_session_config(self):
        """Loads the session configuration from the JSON file."""
        config_path = self.project_root / "config" / "session_config.json"
        if not config_path.exists():
            console.print("⚠️ [yellow]Session config file not found. Session commands may fail.[/yellow]")
            return {}
        with open(config_path, "r") as f:
            return json.load(f)

    def _load_agent_id(self):
        if self.agent_id_file.exists():
            with open(self.agent_id_file, "r") as f:
                try:
                    data = json.load(f)
                    self.agent_id = data.get("agent_id")
                except json.JSONDecodeError:
                    self.agent_id = None

    def _save_agent_id(self):
        with open(self.agent_id_file, "w") as f:
            json.dump({"agent_id": self.agent_id}, f)

    def _register_agent(self):
        self._load_agent_id()
        url = f"{self.comm_api_url}/register"
        payload = {
            "name": self.agent_name,
            "email": self.agent_email
        }
        try:
            console.print(f"🤝 Registering with communication hub...")
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            agent_data = response.json()
            new_agent_id = agent_data.get("id")
            if new_agent_id:
                if self.agent_id != new_agent_id:
                    self.agent_id = new_agent_id
                    self._save_agent_id()
                console.print(f"✅ [green]Registration successful. Agent ID: {self.agent_id}[/green]")
            else:
                console.print("⚠️ [yellow]Registration response did not include an agent ID.[/yellow]")
        except requests.exceptions.RequestException:
            console.print(f"❌ [red]Could not connect to communication hub. Working offline.[/red]")

    def _update_state(self, new_state: Dict):
        if not self.agent_id: return
        url = f"{self.comm_api_url}/state/{self.agent_id}"
        try:
            requests.post(url, json=new_state, timeout=3)
        except requests.exceptions.RequestException: pass

    def _send_broadcast(self, event_type: str, payload: Dict):
        if not self.agent_id: return
        url = f"{self.comm_api_url}/messages"
        message = {
            "sender_id": self.agent_id, "recipient_id": "broadcast",
            "event_type": event_type, "payload": payload
        }
        try:
            requests.post(url, json=message, timeout=3)
        except requests.exceptions.RequestException: pass

    def run_cli_command(self, cli_name: str, command: str, args: List[str] = None) -> int:
        """Run a command from a specific CLI"""
        if cli_name not in self.available_clis:
            console.print(f"❌ [red]Unknown CLI: {cli_name}[/red]")
            return 1
        
        cli_info = self.available_clis[cli_name]
        cli_file = self.project_root / cli_info['file']
        
        if not cli_file.exists():
            console.print(f"❌ [red]CLI file not found: {cli_file}[/red]")
            return 1
        
        # Build command
        cmd = ['python3', str(cli_file)]
        if command != 'interactive':
            cmd.append(command)
        if args:
            cmd.extend(args)
        
        # --- Communication Hub Integration ---
        task_payload = {"cli": cli_name, "command": command, "args": args or []}
        self._update_state({"current_task": task_payload, "status": "starting"})
        self._send_broadcast(event_type="task_started", payload=task_payload)

        try:
            # Run the command
            if cli_name == 'chat' and command == 'interactive':
                # For interactive chat, use subprocess.run without capture
                result_code = subprocess.run(cmd).returncode
                self._send_broadcast(event_type="task_completed", payload={**task_payload, "return_code": result_code})
                return result_code
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout:
                    console.print(result.stdout)
                if result.stderr:
                    console.print(f"[red]{result.stderr}[/red]")

                success = result.returncode == 0
                self._send_broadcast(
                    event_type="task_completed",
                    payload={**task_payload, "return_code": result.returncode, "success": success}
                )
                return result.returncode
        except Exception as e:
            console.print(f"❌ [red]Error running command: {e}[/red]")
            self._send_broadcast(event_type="task_failed", payload={**task_payload, "error": str(e)})
            return 1
        finally:
             self._update_state({"current_task": None, "status": "idle"})
    
    def show_overview(self):
        """Show system overview"""
        console.print(Panel.fit(
            "[bold blue]🚀 GenX Trading Platform - Head CLI[/bold blue]\n"
            "[dim]Unified interface for all trading system components[/dim]",
            border_style="blue"
        ))
        
        # Show available CLIs
        table = Table(title="📋 Available CLI Tools", show_header=True)
        table.add_column("CLI", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Status", style="green")
        
        for cli_name, cli_info in self.available_clis.items():
            cli_file = self.project_root / cli_info['file']
            status = "✅ Available" if cli_file.exists() else "❌ Missing"
            table.add_row(cli_name, cli_info['description'], status)
        
        console.print(table)
        
        # Quick status check
        console.print("\n[bold yellow]🔍 Quick System Check:[/bold yellow]")
        
        # Check AMP authentication
        try:
            result = subprocess.run(['python3', 'amp_cli.py', 'auth', '--status'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "Authenticated as:" in result.stdout:
                console.print("🔐 AMP Authentication: ✅ [green]Active[/green]")
            else:
                console.print("🔐 AMP Authentication: ❌ [red]Not authenticated[/red]")
        except:
            console.print("🔐 AMP Authentication: ⚠️ [yellow]Unknown[/yellow]")
        
        # Check key files
        key_files = ['.env', 'requirements.txt', 'main.py']
        for file_name in key_files:
            file_path = self.project_root / file_name
            status = "✅" if file_path.exists() else "❌"
            console.print(f"📄 {file_name}: {status}")

# Create CLI app instance
head_cli = HeadCLI()


@session_app.command("auth")
def session_auth():
    """Authenticate the device using its build identity."""
    console.print("🔐 Authenticating device...")
    response = session_orchestration.authenticate_device(head_cli.session_config)
    if response:
        console.print("✅ [green]Device authenticated successfully.[/green]")
        console.print(response)
    else:
        console.print("❌ [red]Device authentication failed.[/red]")

@session_app.command("trigger")
def session_trigger(flow_name: str = typer.Argument(..., help="The name of the flow to trigger.")):
    """Trigger an orchestration flow on the session server."""
    console.print(f"🚀 Triggering flow: {flow_name}...")
    response = session_orchestration.trigger_flow(head_cli.session_config, flow_name)
    if response:
        console.print(f"✅ [green]Flow '{flow_name}' triggered successfully.[/green]")
        console.print(response)
    else:
        console.print(f"❌ [red]Failed to trigger flow '{flow_name}'.[/red]")


@session_app.command("sync")
def session_sync(notes_file: str = typer.Argument("notes.json", help="Path to the notes JSON file.")):
    """Sync notes or artifacts to the LiteWriter endpoint."""
    console.print(f"🔄 Syncing notes from {notes_file}...")
    response = session_orchestration.sync_notes(head_cli.session_config, notes_file)
    if response:
        console.print("✅ [green]Notes synced successfully.[/green]")
        console.print(response)
    else:
        console.print("❌ [red]Failed to sync notes.[/red]")


@session_app.command("full-run")
def session_full_run(
    flow_name: str = typer.Argument("sync_notes", help="The name of the flow to trigger."),
    notes_file: str = typer.Argument("notes.json", help="Path to the notes JSON file.")
):
    """Perform a full orchestration run: auth, trigger, and sync."""
    console.print("🏃‍♂️ [bold]Starting full session orchestration run...[/bold]")

    # 1. Authenticate
    console.print("\n[b]Step 1: Authenticating Device[/b]")
    auth_response = session_orchestration.authenticate_device(head_cli.session_config)
    if not auth_response:
        console.print("❌ [red]Authentication failed. Aborting full run.[/red]")
        raise typer.Exit(1)
    console.print("✅ [green]Device authenticated.[/green]")
    console.print(auth_response)

    # 2. Trigger Flow
    console.print(f"\n[b]Step 2: Triggering Flow '{flow_name}'[/b]")
    trigger_response = session_orchestration.trigger_flow(head_cli.session_config, flow_name)
    if not trigger_response:
        console.print(f"❌ [red]Triggering flow '{flow_name}' failed. Aborting.[/red]")
        raise typer.Exit(1)
    console.print(f"✅ [green]Flow '{flow_name}' triggered.[/green]")
    console.print(trigger_response)

    # 3. Sync Notes
    console.print(f"\n[b]Step 3: Syncing Notes from '{notes_file}'[/b]")
    sync_response = session_orchestration.sync_notes(head_cli.session_config, notes_file)
    if not sync_response:
        console.print(f"❌ [red]Syncing notes from '{notes_file}' failed.[/red]")
        raise typer.Exit(1)
    console.print("✅ [green]Notes synced.[/green]")
    console.print(sync_response)

    console.print("\n🏁 [bold green]Full session orchestration run completed successfully![/bold green]")


@app.command()
def overview():
    """Show system overview and status"""
    head_cli.show_overview()

@app.command()
def amp(
    command: str = typer.Argument(help="AMP command to run"),
    args: Optional[List[str]] = typer.Argument(None, help="Additional arguments")
):
    """Run AMP CLI commands - AI models, authentication, monitoring"""
    console.print(f"🤖 [blue]Running AMP command:[/blue] {command}")
    if args:
        console.print(f"   [dim]Args: {' '.join(args)}[/dim]")
    
    exit_code = head_cli.run_cli_command('amp', command, args)
    if exit_code != 0:
        raise typer.Exit(exit_code)

@app.command()
def genx(
    command: str = typer.Argument(help="GenX command to run"),
    args: Optional[List[str]] = typer.Argument(None, help="Additional arguments")
):
    """Run GenX CLI commands - system management, ForexConnect, Excel"""
    console.print(f"⚙️ [green]Running GenX command:[/green] {command}")
    if args:
        console.print(f"   [dim]Args: {' '.join(args)}[/dim]")
    
    exit_code = head_cli.run_cli_command('genx', command, args)
    if exit_code != 0:
        raise typer.Exit(exit_code)

@app.command()
def chat():
    """Start interactive chat with AMP trading system"""
    console.print("💬 [cyan]Starting AMP Chat...[/cyan]")
    exit_code = head_cli.run_cli_command('chat', 'interactive')
    if exit_code != 0:
        raise typer.Exit(exit_code)

@app.command()
def status():
    """Show comprehensive system status"""
    console.print("📊 [bold]System Status Report[/bold]")
    console.print("=" * 50)
    
    # AMP Status
    console.print("\n🤖 [blue]AMP Status:[/blue]")
    head_cli.run_cli_command('amp', 'status')
    
    # GenX Status  
    console.print("\n⚙️ [green]GenX Status:[/green]")
    head_cli.run_cli_command('genx', 'status')

@app.command()
def auth(
    action: str = typer.Option("status", help="Auth action: status, login, logout"),
    token: Optional[str] = typer.Option(None, help="Authentication token for login")
):
    """Manage authentication (shortcut to AMP auth)"""
    if action == "login" and token:
        head_cli.run_cli_command('amp', 'auth', ['--token', token])
    elif action == "logout":
        head_cli.run_cli_command('amp', 'auth', ['--logout'])
    else:
        head_cli.run_cli_command('amp', 'auth', ['--status'])

@app.command()
def init():
    """Initialize the GenX trading system"""
    console.print("🚀 [bold]Initializing GenX Trading System...[/bold]")
    head_cli.run_cli_command('genx', 'init')

@app.command()
def logs(
    source: str = typer.Option("genx", help="Log source: genx, amp, all")
):
    """View system logs"""
    if source == "all":
        console.print("📋 [yellow]All System Logs:[/yellow]")
        head_cli.run_cli_command('genx', 'logs')
    elif source == "genx":
        console.print("📋 [green]GenX Logs:[/green]")
        head_cli.run_cli_command('genx', 'logs')
    else:
        console.print(f"📋 [blue]Logs for {source}:[/blue]")
        head_cli.run_cli_command(source, 'logs')

@app.command()
def monitor():
    """Monitor system performance (AMP monitoring)"""
    console.print("📊 [blue]System Monitoring:[/blue]")
    head_cli.run_cli_command('amp', 'monitor', ['--status'])

@app.command()
def tree():
    """Show project structure tree"""
    console.print("🌳 [green]Project Structure:[/green]")
    head_cli.run_cli_command('genx', 'tree')

@app.command()
def help_all():
    """Show help for all available CLI tools"""
    console.print(Panel.fit(
        "[bold]🆘 Complete Help Guide[/bold]\n"
        "[dim]Available commands across all CLI tools[/dim]",
        border_style="yellow"
    ))
    
    for cli_name, cli_info in head_cli.available_clis.items():
        console.print(f"\n[bold]{cli_name.upper()} CLI:[/bold] {cli_info['description']}")
        
        if cli_name == 'chat':
            console.print("  • interactive - Start interactive chat")
        else:
            for cmd in cli_info['commands']:
                console.print(f"  • {cmd}")
        
        console.print(f"  [dim]Direct access: python3 {cli_info['file']} --help[/dim]")
    
    console.print(f"\n[bold yellow]Head CLI Commands:[/bold yellow]")
    console.print("  • overview - System overview")
    console.print("  • status - Complete system status")
    console.print("  • auth - Authentication management")
    console.print("  • chat - Interactive AMP chat")
    console.print("  • init - Initialize system")
    console.print("  • logs - View logs")
    console.print("  • monitor - System monitoring")
    console.print("  • tree - Project structure")

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
      head_cli session auth          # Authenticate device for session
    """
    if version:
        console.print("GenX Trading Platform Head CLI v1.0.0")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # Show overview if no command provided
        head_cli.show_overview()

if __name__ == "__main__":
    app()