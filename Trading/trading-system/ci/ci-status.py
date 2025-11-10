#!/usr/bin/env python3
"""
CI Status and Management
"""

import os
import json
from datetime import datetime
from pathlib import Path

def check_system_status():
    """Check system components status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "overall": "unknown"
    }
    
    root_dir = Path(__file__).parent.parent
    
    # Check files exist
    critical_files = [
        "trading-signal-generator.py",
        "trading-microservice/src/plugins/mt5-plugin.js",
        "security/credential-manager.js",
        "mt5-fbs-setup/fbs_real_config.json"
    ]
    
    for file in critical_files:
        file_path = root_dir / file
        status["components"][file] = {
            "exists": file_path.exists(),
            "size": file_path.stat().st_size if file_path.exists() else 0
        }
    
    # Check directories
    critical_dirs = [
        "security",
        "mt5-fbs-setup", 
        "trading-analysis",
        "gdrive-scanner"
    ]
    
    for dir_name in critical_dirs:
        dir_path = root_dir / dir_name
        status["components"][f"{dir_name}/"] = {
            "exists": dir_path.exists(),
            "files": len(list(dir_path.rglob("*"))) if dir_path.exists() else 0
        }
    
    # Overall status
    all_critical_exist = all(
        status["components"][file]["exists"] 
        for file in critical_files 
        if file in status["components"]
    )
    
    status["overall"] = "healthy" if all_critical_exist else "issues"
    
    return status

def save_status_report(status):
    """Save status report"""
    with open("ci-status-report.json", 'w') as f:
        json.dump(status, f, indent=2)
    
    print("CI Status Report")
    print("=" * 20)
    print(f"Timestamp: {status['timestamp']}")
    print(f"Overall Status: {status['overall']}")
    print(f"\nComponents:")
    
    for component, info in status["components"].items():
        exists_status = "OK" if info["exists"] else "MISSING"
        if component.endswith("/"):
            print(f"  {component:<30} {exists_status} ({info['files']} files)")
        else:
            print(f"  {component:<30} {exists_status} ({info['size']} bytes)")

def main():
    status = check_system_status()
    save_status_report(status)
    
    if status["overall"] == "healthy":
        print("\nSystem is healthy!")
        return True
    else:
        print("\nSystem has issues!")
        return False

if __name__ == "__main__":
    main()