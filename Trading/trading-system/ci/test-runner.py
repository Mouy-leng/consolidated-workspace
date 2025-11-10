#!/usr/bin/env python3
"""
CI Test Runner for Trading System
"""

import subprocess
import sys
import os
from pathlib import Path

class CITestRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.failed_tests = []
        
    def run_command(self, cmd, cwd=None):
        """Run command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd or self.root_dir,
                capture_output=True, 
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def test_python_syntax(self):
        """Test Python syntax"""
        print("Testing Python syntax...")
        
        python_files = list(self.root_dir.rglob("*.py"))
        for file in python_files:
            success, stdout, stderr = self.run_command(f"python -m py_compile {file}")
            if not success:
                self.failed_tests.append(f"Syntax error in {file}: {stderr}")
                return False
        
        print(f"✅ {len(python_files)} Python files passed syntax check")
        return True
    
    def test_signal_generator(self):
        """Test trading signal generator"""
        print("Testing signal generator...")
        
        test_code = """
import sys
sys.path.append('.')
from trading_signal_generator import TradingSignalGenerator
generator = TradingSignalGenerator()
print('Signal generator test passed')
"""
        
        success, stdout, stderr = self.run_command(f"python -c \"{test_code}\"")
        if not success:
            self.failed_tests.append(f"Signal generator test failed: {stderr}")
            return False
        
        print("✅ Signal generator test passed")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting CI Test Suite")
        print("=" * 30)
        
        tests = [
            self.test_python_syntax,
            self.test_signal_generator
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.failed_tests.append(f"{test.__name__}: {e}")
        
        print(f"\n📊 Test Results: {passed}/{total} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  • {failure}")
            return False
        else:
            print("\n✅ All tests passed!")
            return True

def main():
    runner = CITestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()