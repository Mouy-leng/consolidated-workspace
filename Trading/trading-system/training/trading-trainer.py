#!/usr/bin/env python3
"""
Trading System Training Platform
Interactive learning system for trading concepts and system usage
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class TradingTrainer:
    def __init__(self):
        self.lessons = []
        self.progress = {"completed": [], "score": 0}
        self.load_progress()
        
    def load_progress(self):
        """Load training progress"""
        try:
            with open("training_progress.json", 'r') as f:
                self.progress = json.load(f)
        except:
            self.progress = {"completed": [], "score": 0, "level": "beginner"}
    
    def save_progress(self):
        """Save training progress"""
        with open("training_progress.json", 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def show_menu(self):
        """Show training menu"""
        print("Trading System Training Platform")
        print("=" * 35)
        print("1. Basic Trading Concepts")
        print("2. Technical Analysis")
        print("3. Risk Management")
        print("4. System Usage Training")
        print("5. Live Trading Simulation")
        print("6. Quiz & Assessment")
        print("7. View Progress")
        print("0. Exit")
        
        choice = input("\nSelect training module (0-7): ")
        return choice
    
    def basic_concepts(self):
        """Basic trading concepts training"""
        print("\nBasic Trading Concepts")
        print("=" * 25)
        
        concepts = [
            {
                "title": "What is Forex Trading?",
                "content": """
Forex (Foreign Exchange) is the global market for trading currencies.
- Largest financial market ($6+ trillion daily volume)
- Open 24/5 (Monday to Friday)
- Currency pairs: EUR/USD, GBP/USD, etc.
- Profit from currency price movements
                """,
                "quiz": {
                    "question": "What does EUR/USD = 1.0850 mean?",
                    "options": ["A) 1 EUR = 1.0850 USD", "B) 1 USD = 1.0850 EUR", "C) Both currencies are equal"],
                    "answer": "A"
                }
            },
            {
                "title": "Long vs Short Positions",
                "content": """
LONG (BUY): Expecting price to go UP
- Buy low, sell high
- Profit when price increases

SHORT (SELL): Expecting price to go DOWN  
- Sell high, buy low
- Profit when price decreases
                """,
                "quiz": {
                    "question": "If you think EUR/USD will fall, what do you do?",
                    "options": ["A) Buy EUR/USD", "B) Sell EUR/USD", "C) Wait and see"],
                    "answer": "B"
                }
            },
            {
                "title": "Pips and Spreads",
                "content": """
PIP: Smallest price movement (usually 4th decimal)
- EUR/USD: 1.0850 to 1.0851 = 1 pip

SPREAD: Difference between Bid and Ask
- Bid: 1.0850 (sell price)
- Ask: 1.0852 (buy price)  
- Spread: 2 pips
                """,
                "quiz": {
                    "question": "EUR/USD moves from 1.0850 to 1.0870. How many pips?",
                    "options": ["A) 2 pips", "B) 20 pips", "C) 200 pips"],
                    "answer": "B"
                }
            }
        ]
        
        for i, concept in enumerate(concepts):
            print(f"\nLesson {i+1}: {concept['title']}")
            print(concept['content'])
            
            # Quiz
            print(f"\nQuiz: {concept['quiz']['question']}")
            for option in concept['quiz']['options']:
                print(f"  {option}")
            
            answer = input("Your answer: ").upper()
            if answer == concept['quiz']['answer']:
                print("Correct! Well done.")
                self.progress['score'] += 10
            else:
                print(f"Incorrect. The answer is {concept['quiz']['answer']}")
            
            input("Press Enter to continue...")
        
        self.progress['completed'].append('basic_concepts')
        self.save_progress()
    
    def technical_analysis(self):
        """Technical analysis training"""
        print("\nTechnical Analysis Training")
        print("=" * 30)
        
        # Generate sample data for demonstration
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        prices = 1.0800 + np.cumsum(np.random.randn(50) * 0.001)
        data = pd.DataFrame({'Close': prices}, index=dates)
        
        # Calculate indicators
        data['RSI'] = self.calculate_rsi_demo(data['Close'])
        data['MA20'] = data['Close'].rolling(20).mean()
        
        print("RSI (Relative Strength Index):")
        print("- Measures overbought/oversold conditions")
        print("- Range: 0-100")
        print("- RSI > 70: Overbought (potential sell)")
        print("- RSI < 30: Oversold (potential buy)")
        
        current_rsi = data['RSI'].iloc[-1]
        print(f"\nCurrent RSI: {current_rsi:.1f}")
        
        if current_rsi > 70:
            print("Signal: OVERBOUGHT - Consider selling")
        elif current_rsi < 30:
            print("Signal: OVERSOLD - Consider buying")
        else:
            print("Signal: NEUTRAL - No clear signal")
        
        # Quiz
        print(f"\nQuiz: If RSI is 25, what does this suggest?")
        print("A) Overbought - sell signal")
        print("B) Oversold - buy signal") 
        print("C) Neutral - no signal")
        
        answer = input("Your answer: ").upper()
        if answer == "B":
            print("Correct! RSI < 30 suggests oversold conditions.")
            self.progress['score'] += 15
        else:
            print("Incorrect. RSI < 30 indicates oversold (buy signal).")
        
        self.progress['completed'].append('technical_analysis')
        self.save_progress()
    
    def risk_management(self):
        """Risk management training"""
        print("\nRisk Management Training")
        print("=" * 28)
        
        scenarios = [
            {
                "title": "Position Sizing",
                "scenario": "Account: $1000, Risk per trade: 2%, Stop loss: 50 pips",
                "question": "What lot size should you use?",
                "calculation": "Risk amount = $1000 × 2% = $20\nPer pip value needed = $20 ÷ 50 pips = $0.40\nLot size = 0.04 lots (micro lots)",
                "answer": "0.04 lots"
            },
            {
                "title": "Risk-Reward Ratio",
                "scenario": "Entry: 1.0850, Stop Loss: 1.0830, Take Profit: 1.0890",
                "question": "What's the risk-reward ratio?",
                "calculation": "Risk = 1.0850 - 1.0830 = 20 pips\nReward = 1.0890 - 1.0850 = 40 pips\nRatio = 40:20 = 2:1",
                "answer": "2:1"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['title']}:")
            print(f"Scenario: {scenario['scenario']}")
            print(f"Question: {scenario['question']}")
            
            user_answer = input("Your answer: ")
            
            print(f"\nCalculation:")
            print(scenario['calculation'])
            print(f"Correct answer: {scenario['answer']}")
            
            if user_answer.lower() in scenario['answer'].lower():
                print("Excellent! You understand risk management.")
                self.progress['score'] += 20
            else:
                print("Review the calculation above.")
            
            input("Press Enter to continue...")
        
        self.progress['completed'].append('risk_management')
        self.save_progress()
    
    def system_usage(self):
        """System usage training"""
        print("\nSystem Usage Training")
        print("=" * 25)
        
        modules = [
            {
                "title": "Running Signal Generator",
                "steps": [
                    "1. Open terminal/command prompt",
                    "2. Navigate to trading-system folder",
                    "3. Run: python trading-signal-generator.py",
                    "4. Monitor generated signals",
                    "5. Review signal quality and timing"
                ]
            },
            {
                "title": "Using MT4 Bot",
                "steps": [
                    "1. Ensure MT4 is running and logged in",
                    "2. Navigate to mt4-fbs-setup folder", 
                    "3. Run: python mt4-trading-bot.py",
                    "4. Monitor bot performance",
                    "5. Check positions and P&L"
                ]
            },
            {
                "title": "Security Management",
                "steps": [
                    "1. Run: node setup-security.js",
                    "2. Enter credentials securely",
                    "3. Test VPS connection",
                    "4. Verify encrypted storage",
                    "5. Monitor system health"
                ]
            }
        ]
        
        for module in modules:
            print(f"\n{module['title']}:")
            for step in module['steps']:
                print(f"  {step}")
            
            completed = input(f"\nHave you completed {module['title']}? (y/n): ")
            if completed.lower() == 'y':
                self.progress['score'] += 10
        
        self.progress['completed'].append('system_usage')
        self.save_progress()
    
    def live_simulation(self):
        """Live trading simulation"""
        print("\nLive Trading Simulation")
        print("=" * 27)
        
        balance = 1000.0
        trades = []
        
        print(f"Starting balance: ${balance:.2f}")
        print("You'll make 5 simulated trades based on signals.")
        
        for i in range(5):
            # Generate random market scenario
            symbol = random.choice(["EURUSD", "GBPUSD", "XAUUSD"])
            price = round(random.uniform(1.0500, 1.1000), 5)
            rsi = random.randint(20, 80)
            
            print(f"\nTrade {i+1}:")
            print(f"Symbol: {symbol}")
            print(f"Current Price: {price}")
            print(f"RSI: {rsi}")
            
            if rsi < 30:
                suggestion = "BUY (RSI Oversold)"
            elif rsi > 70:
                suggestion = "SELL (RSI Overbought)"
            else:
                suggestion = "WAIT (No clear signal)"
            
            print(f"Suggested Action: {suggestion}")
            
            action = input("Your decision (BUY/SELL/WAIT): ").upper()
            
            if action in ["BUY", "SELL"]:
                lots = 0.01
                # Simulate outcome
                outcome = random.choice(["profit", "loss"])
                pnl = random.uniform(-20, 30) if outcome == "profit" else random.uniform(-30, -5)
                
                balance += pnl
                trades.append({
                    "symbol": symbol,
                    "action": action,
                    "price": price,
                    "pnl": pnl,
                    "balance": balance
                })
                
                print(f"Result: {outcome.upper()}")
                print(f"P&L: ${pnl:.2f}")
                print(f"New Balance: ${balance:.2f}")
                
                if action == suggestion.split()[0]:
                    print("Good decision! You followed the signal.")
                    self.progress['score'] += 5
            else:
                print("You chose to wait. Sometimes patience is key!")
        
        print(f"\nSimulation Complete!")
        print(f"Final Balance: ${balance:.2f}")
        print(f"Total P&L: ${balance - 1000:.2f}")
        
        self.progress['completed'].append('live_simulation')
        self.save_progress()
    
    def calculate_rsi_demo(self, prices, period=14):
        """Calculate RSI for demo"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def quiz_assessment(self):
        """Comprehensive quiz"""
        print("\nTrading Knowledge Assessment")
        print("=" * 32)
        
        questions = [
            {
                "q": "What is the main risk in forex trading?",
                "options": ["A) Currency fluctuation", "B) Broker fees", "C) Internet connection"],
                "answer": "A"
            },
            {
                "q": "Best risk per trade for beginners?",
                "options": ["A) 10%", "B) 2%", "C) 50%"],
                "answer": "B"
            },
            {
                "q": "RSI above 70 indicates?",
                "options": ["A) Oversold", "B) Overbought", "C) Neutral"],
                "answer": "B"
            },
            {
                "q": "What's a good risk-reward ratio?",
                "options": ["A) 1:1", "B) 1:2", "C) 2:1"],
                "answer": "B"
            }
        ]
        
        score = 0
        for i, q in enumerate(questions):
            print(f"\nQuestion {i+1}: {q['q']}")
            for option in q['options']:
                print(f"  {option}")
            
            answer = input("Your answer: ").upper()
            if answer == q['answer']:
                print("Correct!")
                score += 25
            else:
                print(f"Incorrect. Answer: {q['answer']}")
        
        print(f"\nQuiz Score: {score}/100")
        
        if score >= 75:
            print("Excellent! You're ready for live trading.")
            self.progress['level'] = 'advanced'
        elif score >= 50:
            print("Good! Continue practicing.")
            self.progress['level'] = 'intermediate'
        else:
            print("Keep studying. Review the basics.")
            self.progress['level'] = 'beginner'
        
        self.progress['score'] += score
        self.save_progress()
    
    def view_progress(self):
        """View training progress"""
        print("\nTraining Progress")
        print("=" * 20)
        print(f"Level: {self.progress.get('level', 'beginner').title()}")
        print(f"Total Score: {self.progress['score']}")
        print(f"Completed Modules: {len(self.progress['completed'])}")
        
        modules = ['basic_concepts', 'technical_analysis', 'risk_management', 
                  'system_usage', 'live_simulation']
        
        for module in modules:
            status = "✓" if module in self.progress['completed'] else "○"
            print(f"  {status} {module.replace('_', ' ').title()}")
    
    def run(self):
        """Run training platform"""
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.basic_concepts()
            elif choice == "2":
                self.technical_analysis()
            elif choice == "3":
                self.risk_management()
            elif choice == "4":
                self.system_usage()
            elif choice == "5":
                self.live_simulation()
            elif choice == "6":
                self.quiz_assessment()
            elif choice == "7":
                self.view_progress()
            elif choice == "0":
                print("Training complete! Happy trading!")
                break
            else:
                print("Invalid choice. Try again.")

def main():
    trainer = TradingTrainer()
    trainer.run()

if __name__ == "__main__":
    main()