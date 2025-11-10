#!/usr/bin/env python3
"""
Simple CI Test Runner
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run basic tests"""
    print("Starting CI Test Suite")
    print("=" * 25)
    
    root_dir = Path(__file__).parent.parent
    failed_tests = []
    
    # Test Python syntax
    print("Testing Python syntax...")
    python_files = list(root_dir.rglob("*.py"))
    
    for file in python_files:
        try:
            result = subprocess.run(
                f"python -m py_compile {file}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                failed_tests.append(f"Syntax error in {file}")
        except Exception as e:
            failed_tests.append(f"Error testing {file}: {e}")
    
    print(f"Checked {len(python_files)} Python files")
    
    # Test signal generator
    print("Testing signal generator...")
    try:
        result = subprocess.run(
            "python -c \"from trading_signal_generator import TradingSignalGenerator; print('OK')\"",
            shell=True,
            cwd=root_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            failed_tests.append("Signal generator import failed")
    except Exception as e:
        failed_tests.append(f"Signal generator test error: {e}")
    
    # Results
    if failed_tests:
        print("\nFailed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
        return False
    else:
        print("\nAll tests passed!")
        return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)