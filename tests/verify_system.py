"""
tests/verify_system.py
The System Doctor: Comprehensive self-test for ZeroCrate architecture.
Verifies File Structure, Imports, and Web API functionality.
"""

import sys
import os
import importlib
from pathlib import Path
from fastapi.testclient import TestClient
from rich.console import Console
from rich.table import Table

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

console = Console()

def print_header(text):
    console.print(f"\n[bold cyan]=== {text} ===[/bold cyan]")

def check_structure():
    print_header("Phase 1: Structural Integrity")
    
    required_paths = [
        "core",
        "core/ledger.py",
        "core/models.py",
        "core/inventory.py",
        "miners",
        "miners/scout.py",
        "backend",
        "backend/main.py",
        "backend/templates/index.html",
        "backend/static/style.css",
        "data"
    ]
    
    table = Table(title="Filesystem Check")
    table.add_column("Path", style="white")
    table.add_column("Status", style="bold")
    
    all_passed = True
    root = Path(".")
    
    for p in required_paths:
        path = root / p
        if path.exists():
            table.add_row(p, "[green]OK[/green]")
        else:
            table.add_row(p, "[red]MISSING[/red]")
            all_passed = False
            
    console.print(table)
    return all_passed

def check_imports():
    print_header("Phase 2: Neural Connections (Imports)")
    
    modules = [
        "core.ledger",
        "core.models",
        "core.inventory",
        "backend.main",
        "miners.scout"
    ]
    
    all_passed = True
    for mod in modules:
        try:
            importlib.import_module(mod)
            console.print(f"✅ Import [bold]{mod}[/bold]: [green]SUCCESS[/green]")
        except ImportError as e:
            console.print(f"❌ Import [bold]{mod}[/bold]: [red]FAILED[/red] ({e})")
            all_passed = False
            
    return all_passed

def check_web_api():
    print_header("Phase 3: Web Systems (API)")
    
    # Delayed import to avoid crashing if Structure Check failed
    try:
        from backend.main import app
        client = TestClient(app)
        all_passed = True
        
        # 1. Home Page
        response = client.get("/")
        if response.status_code == 200:
            console.print("✅ GET / (Dashboard): [green]ONLINE[/green]")
        else:
            console.print(f"❌ GET / (Dashboard): [red]FAILED[/red] ({response.status_code})")
            all_passed = False

        # 2. State (The Unified Endpoint)
        response = client.get("/api/state")
        if response.status_code == 200:
            data = response.json()
            # Phase 12 Contract: { scout, hero, rails }
            if "scout" in data and "hero" in data and "rails" in data:
                 console.print(f"✅ GET /api/state: [green]OK[/green] (Lvl {data['hero']['level']})")
                 rails = data['rails']
                 if isinstance(rails, list) and len(rails) >= 5:
                     console.print(f"✅ Rails Structure: [green]OK[/green] ({len(rails)} rails)")
                 else:
                     console.print(f"❌ Rails Structure: [red]MALFORMED[/red] (Expected list of >=5 rails)")
                     all_passed = False
            else:
                 console.print(f"❌ GET /api/state: [red]MALFORMED[/red] (Missing root keys: scout/hero/rails)")
                 all_passed = False
        else:
            console.print(f"❌ GET /api/state: [red]FAILED[/red] ({response.status_code})")
            all_passed = False
            
        return all_passed

    except Exception as e:
        console.print(f"❌ Web API Critical Failure: {e}")
        return False

def main():
    console.print("[dim]Starting System Diagnostics...[/dim]")
    
    if not check_structure():
        console.print("\n[bold red]FATAL: Structural Integrity Compromised.[/bold red]")
        sys.exit(1)
        
    if not check_imports():
        console.print("\n[bold red]FATAL: Import Errors Detected.[/bold red]")
        sys.exit(1)
        
    if not check_web_api():
        console.print("\n[bold red]FATAL: Web Systems Malfunction.[/bold red]")
        sys.exit(1)
        
    console.print("\n[bold green]ALL SYSTEMS NOMINAL. READY FOR DEPLOYMENT.[/bold green] 🚀")

if __name__ == "__main__":
    main()
