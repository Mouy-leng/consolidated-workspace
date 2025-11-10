#!/usr/bin/env python3
"""
Simple Training Progress Checker
"""

import json
import os

def check_progress():
    """Check training progress"""
    print("Trading System Training Progress")
    print("=" * 35)
    
    try:
        with open("training_progress.json", 'r') as f:
            progress = json.load(f)
    except:
        progress = {"completed": [], "score": 0, "level": "beginner"}
    
    print(f"Current Level: {progress.get('level', 'beginner').title()}")
    print(f"Total Score: {progress.get('score', 0)} points")
    print(f"Completed Modules: {len(progress.get('completed', []))}")
    
    modules = [
        ('basic_concepts', 'Basic Trading Concepts'),
        ('technical_analysis', 'Technical Analysis'),
        ('risk_management', 'Risk Management'),
        ('system_usage', 'System Usage Training'),
        ('live_simulation', 'Live Trading Simulation')
    ]
    
    print(f"\nModule Progress:")
    for module_id, module_name in modules:
        if module_id in progress.get('completed', []):
            status = "[COMPLETED]"
        else:
            status = "[NOT STARTED]"
        print(f"  {status} {module_name}")
    
    # Recommendations
    completed_count = len(progress.get('completed', []))
    
    print(f"\nRecommendations:")
    if completed_count == 0:
        print("  - Start with 'Basic Trading Concepts'")
        print("  - Run: python training/trading-trainer.py")
    elif completed_count < 3:
        print("  - Continue with fundamental modules")
        print("  - Focus on risk management")
    elif completed_count < 5:
        print("  - Complete all basic modules")
        print("  - Try practice scenarios")
    else:
        print("  - Try advanced strategies")
        print("  - Run advanced training modules")
    
    print(f"\nAvailable Training:")
    print("  1. Complete Course: python training/trading-trainer.py")
    print("  2. Practice Scenarios: python training/exercises/practice-scenarios.py")
    print("  3. Advanced Strategies: python training/modules/advanced-strategies.py")
    print("  4. Quick Launcher: powershell training/start-training.ps1")

if __name__ == "__main__":
    check_progress()