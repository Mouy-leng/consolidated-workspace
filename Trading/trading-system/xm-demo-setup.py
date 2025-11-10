#!/usr/bin/env python3
"""
XM Demo Account Setup and Testing System
Helps compare XM vs FBS broker performance
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta
import logging

# Fix Windows Unicode issues
sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xm_demo_testing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class XMDemoTester:
    def __init__(self):
        self.demo_account = {
            'server': 'XMGlobal-Demo',
            'login': None,
            'password': None,
            'balance': 10000.0,  # Demo balance
            'leverage': '1:888'
        }
        self.test_results = {
            'spreads': {},
            'execution_time': {},
            'slippage': {},
            'connection_quality': {}
        }
        
    def setup_demo_account(self):
        """Guide user through XM demo account setup"""
        print("🦊 XM DEMO ACCOUNT SETUP")
        print("=" * 50)
        
        print("\n📋 STEP 1: Visit XM Demo Registration")
        print("🌐 URL: https://www.xm.com/register/demo")
        
        print("\n📝 STEP 2: Fill Demo Account Form")
        print("   ✅ Account Type: Standard (similar to FBS)")
        print("   ✅ Platform: MT4 or MT5 (your choice)")
        print("   ✅ Leverage: 1:888 (high leverage like FBS)")
        print("   ✅ Base Currency: USD")
        print("   ✅ Demo Balance: $10,000")
        
        print("\n📧 STEP 3: Check Email for Login Details")
        print("   ✅ Server: XMGlobal-Demo")
        print("   ✅ Login: (will be provided)")
        print("   ✅ Password: (will be provided)")
        
        print("\n💾 STEP 4: Download MetaTrader")
        print("   🔗 MT4: https://download.mql5.com/cdn/web/xm.global.limited/mt4/xmglobal4setup.exe")
        print("   🔗 MT5: https://download.mql5.com/cdn/web/xm.global.limited/mt5/xmglobal5setup.exe")
        
        # Get user input for demo account details
        print("\n🔑 ENTER YOUR DEMO ACCOUNT DETAILS:")
        login = input("Demo Login Number: ").strip()
        password = input("Demo Password: ").strip()
        
        if login and password:
            self.demo_account['login'] = login
            self.demo_account['password'] = password
            self.save_demo_config()
            print("✅ Demo account configured successfully!")
            return True
        else:
            print("❌ Please complete XM demo registration first")
            return False
    
    def save_demo_config(self):
        """Save demo account configuration"""
        config = {
            'xm_demo': self.demo_account,
            'setup_date': datetime.now().isoformat(),
            'test_results': self.test_results
        }
        
        with open('xm_demo_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Config saved to xm_demo_config.json")
    
    def load_demo_config(self):
        """Load existing demo account configuration"""
        try:
            with open('xm_demo_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.demo_account = config.get('xm_demo', self.demo_account)
                self.test_results = config.get('test_results', self.test_results)
                return True
        except FileNotFoundError:
            return False
    
    def test_spreads_comparison(self):
        """Compare spreads between XM and FBS"""
        print("\n📊 SPREAD COMPARISON TEST")
        print("=" * 40)
        
        # Major currency pairs to test
        pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        
        spread_comparison = {
            'timestamp': datetime.now().isoformat(),
            'pairs': {}
        }
        
        for pair in pairs:
            print(f"\n💱 Testing {pair}:")
            
            # FBS spread (user input since we can't access live data)
            fbs_spread = input(f"   📈 Current FBS {pair} spread (pips): ").strip()
            xm_spread = input(f"   🦊 Current XM {pair} spread (pips): ").strip()
            
            try:
                fbs_val = float(fbs_spread) if fbs_spread else 0
                xm_val = float(xm_spread) if xm_spread else 0
                
                spread_comparison['pairs'][pair] = {
                    'fbs_spread': fbs_val,
                    'xm_spread': xm_val,
                    'difference': xm_val - fbs_val,
                    'winner': 'XM' if xm_val < fbs_val else 'FBS' if fbs_val < xm_val else 'TIE'
                }
                
                diff = xm_val - fbs_val
                if diff < 0:
                    print(f"   ✅ XM BETTER by {abs(diff):.1f} pips")
                elif diff > 0:
                    print(f"   ❌ FBS BETTER by {diff:.1f} pips")
                else:
                    print(f"   🤝 SAME spread")
                    
            except ValueError:
                print(f"   ⚠️  Skipping {pair} - invalid input")
        
        # Save results
        self.test_results['spreads'] = spread_comparison
        self.save_demo_config()
        
        return spread_comparison
    
    def test_execution_speed(self):
        """Test order execution speed comparison"""
        print("\n⚡ EXECUTION SPEED TEST")
        print("=" * 40)
        
        print("📝 Manual Testing Instructions:")
        print("1. Open small orders on both FBS and XM demo")
        print("2. Time how long each takes to execute")
        print("3. Test during different market conditions")
        
        execution_test = {
            'timestamp': datetime.now().isoformat(),
            'tests': []
        }
        
        test_count = 3
        for i in range(test_count):
            print(f"\n🔄 Test {i+1}/{test_count}:")
            
            fbs_time = input("   ⏱️  FBS execution time (seconds): ").strip()
            xm_time = input("   ⏱️  XM execution time (seconds): ").strip()
            
            try:
                fbs_val = float(fbs_time) if fbs_time else 0
                xm_val = float(xm_time) if xm_time else 0
                
                test_result = {
                    'test_number': i+1,
                    'fbs_execution': fbs_val,
                    'xm_execution': xm_val,
                    'difference': xm_val - fbs_val,
                    'winner': 'XM' if xm_val < fbs_val else 'FBS' if fbs_val < xm_val else 'TIE'
                }
                
                execution_test['tests'].append(test_result)
                
                diff = xm_val - fbs_val
                if diff < 0:
                    print(f"   ✅ XM FASTER by {abs(diff):.2f}s")
                elif diff > 0:
                    print(f"   ❌ FBS FASTER by {diff:.2f}s")
                else:
                    print(f"   🤝 SAME speed")
                    
            except ValueError:
                print(f"   ⚠️  Skipping test {i+1} - invalid input")
        
        # Calculate averages
        if execution_test['tests']:
            fbs_avg = sum(t['fbs_execution'] for t in execution_test['tests']) / len(execution_test['tests'])
            xm_avg = sum(t['xm_execution'] for t in execution_test['tests']) / len(execution_test['tests'])
            
            execution_test['summary'] = {
                'fbs_average': fbs_avg,
                'xm_average': xm_avg,
                'overall_winner': 'XM' if xm_avg < fbs_avg else 'FBS'
            }
            
            print(f"\n📊 SUMMARY:")
            print(f"   FBS Average: {fbs_avg:.2f}s")
            print(f"   XM Average: {xm_avg:.2f}s")
            print(f"   🏆 Winner: {execution_test['summary']['overall_winner']}")
        
        self.test_results['execution_time'] = execution_test
        self.save_demo_config()
        
        return execution_test
    
    def generate_comparison_report(self):
        """Generate comprehensive comparison report"""
        print("\n📋 GENERATING COMPARISON REPORT")
        print("=" * 50)
        
        report = {
            'test_date': datetime.now().isoformat(),
            'account_info': {
                'fbs_balance': 47.79,
                'xm_demo_balance': 10000.0,
                'test_purpose': 'Broker migration evaluation'
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        # Save detailed report
        filename = f"xm_fbs_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved: {filename}")
        
        # Print summary
        self.print_summary_report(report)
        
        return report
    
    def generate_recommendations(self):
        """Generate broker recommendations based on test results"""
        recommendations = {
            'immediate_action': [],
            'long_term_strategy': [],
            'risk_assessment': {}
        }
        
        # Analyze spread results
        if 'spreads' in self.test_results and self.test_results['spreads'].get('pairs'):
            xm_wins = sum(1 for pair in self.test_results['spreads']['pairs'].values() 
                         if pair.get('winner') == 'XM')
            total_pairs = len(self.test_results['spreads']['pairs'])
            
            if xm_wins > total_pairs / 2:
                recommendations['immediate_action'].append("✅ XM shows better spreads - consider migration")
            else:
                recommendations['immediate_action'].append("⚠️ FBS competitive on spreads - evaluate other factors")
        
        # Analyze execution speed
        if 'execution_time' in self.test_results and self.test_results['execution_time'].get('summary'):
            winner = self.test_results['execution_time']['summary'].get('overall_winner')
            if winner == 'XM':
                recommendations['immediate_action'].append("✅ XM faster execution - good for scalping")
            else:
                recommendations['immediate_action'].append("⚠️ FBS faster execution - current setup optimal")
        
        # Strategic recommendations
        recommendations['long_term_strategy'] = [
            "🎯 Test both platforms with $50-100 live accounts",
            "📊 Compare actual trading results over 2 weeks",
            "💰 Evaluate deposit/withdrawal processes",
            "🔒 Assess customer support quality",
            "🚀 Consider FTMO evaluation for scaling"
        ]
        
        return recommendations
    
    def print_summary_report(self, report):
        """Print formatted summary report"""
        print("\n🏆 XM vs FBS COMPARISON SUMMARY")
        print("=" * 60)
        
        # Spread analysis
        if report['test_results'].get('spreads', {}).get('pairs'):
            print("\n💱 SPREAD ANALYSIS:")
            pairs = report['test_results']['spreads']['pairs']
            xm_wins = sum(1 for p in pairs.values() if p.get('winner') == 'XM')
            fbs_wins = sum(1 for p in pairs.values() if p.get('winner') == 'FBS')
            ties = len(pairs) - xm_wins - fbs_wins
            
            print(f"   🦊 XM Better: {xm_wins} pairs")
            print(f"   📈 FBS Better: {fbs_wins} pairs")
            print(f"   🤝 Ties: {ties} pairs")
        
        # Execution analysis
        if report['test_results'].get('execution_time', {}).get('summary'):
            exec_summary = report['test_results']['execution_time']['summary']
            print(f"\n⚡ EXECUTION SPEED:")
            print(f"   🦊 XM Average: {exec_summary['xm_average']:.2f}s")
            print(f"   📈 FBS Average: {exec_summary['fbs_average']:.2f}s")
            print(f"   🏆 Winner: {exec_summary['overall_winner']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']['immediate_action']:
            print(f"   {rec}")
        
        print(f"\n🎯 NEXT STEPS:")
        for step in report['recommendations']['long_term_strategy'][:3]:
            print(f"   {step}")

def main():
    print("🦊 XM DEMO TESTING SYSTEM")
    print("=" * 50)
    print("Testing XM vs FBS broker comparison")
    
    tester = XMDemoTester()
    
    # Load existing config or setup new
    if tester.load_demo_config():
        print("✅ Loaded existing XM demo configuration")
    else:
        print("🆕 Setting up new XM demo account")
        if not tester.setup_demo_account():
            return
    
    while True:
        print("\n🔧 XM TESTING MENU:")
        print("1. 📊 Test Spread Comparison")
        print("2. ⚡ Test Execution Speed")
        print("3. 📋 Generate Comparison Report")
        print("4. 🔧 Reconfigure Demo Account")
        print("5. 🚪 Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            tester.test_spreads_comparison()
        elif choice == '2':
            tester.test_execution_speed()
        elif choice == '3':
            tester.generate_comparison_report()
        elif choice == '4':
            tester.setup_demo_account()
        elif choice == '5':
            print("👋 Testing complete!")
            break
        else:
            print("❌ Invalid option, please try again")

if __name__ == "__main__":
    main()