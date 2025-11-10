#!/usr/bin/env python3
"""
Trading Practice Scenarios
Real-world trading situations for practice
"""

import random
import json
from datetime import datetime

class PracticeScenarios:
    def __init__(self):
        self.scenarios = []
        self.results = []
        
    def scenario_1_trend_following(self):
        """Trend following scenario"""
        print("Scenario 1: Trend Following")
        print("=" * 30)
        
        print("""
Market Situation:
- EURUSD has been in uptrend for 2 weeks
- Price above 20 and 50 MA
- RSI: 45 (neutral)
- Current price: 1.0850
- Recent pullback to 1.0830 (support held)

Technical Setup:
- Support: 1.0830
- Resistance: 1.0880
- Trend: Bullish
        """)
        
        print("What's your trading decision?")
        print("A) Buy at current price (1.0850)")
        print("B) Wait for pullback to 1.0830")
        print("C) Sell expecting reversal")
        print("D) Wait for breakout above 1.0880")
        
        decision = input("Your decision (A/B/C/D): ").upper()
        
        explanations = {
            "A": "Good choice! Buying in uptrend with support holding.",
            "B": "Conservative approach. Waiting for better entry.",
            "C": "Risky! Going against established trend.",
            "D": "Valid strategy. Waiting for momentum confirmation."
        }
        
        print(f"\nYour choice: {explanations.get(decision, 'Invalid choice')}")
        
        # Simulate outcome
        if decision in ["A", "B", "D"]:
            outcome = "Price moved to 1.0890 (+40 pips profit)"
            score = 10
        else:
            outcome = "Price continued up to 1.0890 (-40 pips loss)"
            score = 0
        
        print(f"Outcome: {outcome}")
        return score
    
    def scenario_2_news_trading(self):
        """News trading scenario"""
        print("\nScenario 2: News Trading")
        print("=" * 28)
        
        print("""
Market Situation:
- USD Non-Farm Payrolls in 5 minutes
- Expected: 200K, Previous: 180K
- EURUSD: 1.0850 (range-bound)
- Volatility expected to spike

Pre-News Setup:
- Support: 1.0830
- Resistance: 1.0870
- Current spread: 3 pips (widening)
        """)
        
        print("How do you handle this news event?")
        print("A) Buy before news (expecting good data)")
        print("B) Sell before news (expecting bad data)")
        print("C) Wait for news, then trade breakout")
        print("D) Stay out completely")
        
        decision = input("Your decision (A/B/C/D): ").upper()
        
        # Simulate news outcome
        actual_nfp = random.choice([150, 250])  # Bad or good news
        
        if actual_nfp > 200:
            market_reaction = "USD strengthened, EURUSD fell to 1.0810"
            if decision == "B":
                result = "Correct prediction! +40 pips profit"
                score = 15
            elif decision == "C":
                result = "Caught the breakout! +30 pips profit"
                score = 12
            else:
                result = "Wrong direction or missed opportunity"
                score = 0
        else:
            market_reaction = "USD weakened, EURUSD rose to 1.0890"
            if decision == "A":
                result = "Correct prediction! +40 pips profit"
                score = 15
            elif decision == "C":
                result = "Caught the breakout! +30 pips profit"
                score = 12
            else:
                result = "Wrong direction or missed opportunity"
                score = 0
        
        print(f"\nNews Result: NFP = {actual_nfp}K")
        print(f"Market Reaction: {market_reaction}")
        print(f"Your Result: {result}")
        
        return score
    
    def scenario_3_risk_management(self):
        """Risk management scenario"""
        print("\nScenario 3: Risk Management")
        print("=" * 31)
        
        print("""
Your Trading Account:
- Balance: $5,000
- Risk per trade: 2% ($100)
- Open positions: 2 trades (-$80 total)

New Opportunity:
- GBPUSD setup with 50 pip stop loss
- High probability trade (80% confidence)
- Potential reward: 100 pips
        """)
        
        print("What position size do you take?")
        print("A) 0.20 lots (normal size)")
        print("B) 0.10 lots (reduced size)")
        print("C) 0.30 lots (increased size)")
        print("D) Skip the trade")
        
        decision = input("Your decision (A/B/C/D): ").upper()
        
        # Calculate correct position size
        # Risk = $100, Stop = 50 pips
        # Per pip value needed = $100 / 50 = $2
        # Lot size = $2 / $10 (standard lot pip value) = 0.20 lots
        
        correct_size = 0.20
        
        explanations = {
            "A": f"Correct! $100 risk ÷ 50 pips = 0.20 lots",
            "B": f"Too conservative. You're under-risking.",
            "C": f"Too aggressive! This exceeds your 2% risk rule.",
            "D": f"Missing good opportunities hurts long-term profits."
        }
        
        print(f"\nExplanation: {explanations.get(decision, 'Invalid choice')}")
        
        if decision == "A":
            score = 15
        elif decision == "B":
            score = 8
        else:
            score = 0
        
        return score
    
    def scenario_4_psychology(self):
        """Trading psychology scenario"""
        print("\nScenario 4: Trading Psychology")
        print("=" * 34)
        
        print("""
Situation:
- You've had 3 losing trades in a row (-$300)
- Feeling frustrated and angry
- New setup appears (similar to previous losses)
- Account balance: $4,700

Emotional State:
- Wanting to "get even" quickly
- Considering larger position size
- Doubting your strategy
        """)
        
        print("What's the best psychological approach?")
        print("A) Take larger position to recover losses quickly")
        print("B) Skip trading today, review what went wrong")
        print("C) Take normal position size, stick to plan")
        print("D) Reduce position size until confidence returns")
        
        decision = input("Your decision (A/B/C/D): ").upper()
        
        explanations = {
            "A": "Dangerous! Revenge trading leads to bigger losses.",
            "B": "Wise choice. Taking a break prevents emotional decisions.",
            "C": "Good discipline. Sticking to plan despite emotions.",
            "D": "Conservative approach. Rebuilding confidence gradually."
        }
        
        print(f"\nPsychological Analysis: {explanations.get(decision, 'Invalid choice')}")
        
        if decision in ["B", "C", "D"]:
            print("You demonstrated good emotional control!")
            score = 12
        else:
            print("Emotional trading is the fastest way to lose money.")
            score = 0
        
        return score
    
    def scenario_5_market_conditions(self):
        """Market conditions scenario"""
        print("\nScenario 5: Market Conditions")
        print("=" * 33)
        
        print("""
Market Environment:
- Low volatility period (summer doldrums)
- Major pairs in tight ranges
- Economic calendar is light
- Spreads are normal

EURUSD Analysis:
- 20-day range: 1.0830 - 1.0870
- Current: 1.0850 (middle of range)
- Volume: Below average
- No clear trend
        """)
        
        print("Best strategy for this environment?")
        print("A) Range trading (buy support, sell resistance)")
        print("B) Breakout trading (wait for range break)")
        print("C) Trend following (look for momentum)")
        print("D) Stay out of markets")
        
        decision = input("Your decision (A/B/C/D): ").upper()
        
        explanations = {
            "A": "Perfect! Range trading works best in low volatility.",
            "B": "Risky. Breakouts often fail in low volatility.",
            "C": "Difficult. No clear trends in ranging markets.",
            "D": "Conservative but misses opportunities."
        }
        
        print(f"\nStrategy Analysis: {explanations.get(decision, 'Invalid choice')}")
        
        if decision == "A":
            score = 15
        elif decision == "D":
            score = 8
        else:
            score = 3
        
        return score
    
    def run_practice_session(self):
        """Run complete practice session"""
        print("Trading Practice Scenarios")
        print("=" * 30)
        print("Test your trading skills in realistic situations!\n")
        
        scenarios = [
            self.scenario_1_trend_following,
            self.scenario_2_news_trading,
            self.scenario_3_risk_management,
            self.scenario_4_psychology,
            self.scenario_5_market_conditions
        ]
        
        total_score = 0
        max_score = 67  # Maximum possible points
        
        for i, scenario in enumerate(scenarios):
            print(f"\n{'='*50}")
            score = scenario()
            total_score += score
            print(f"Scenario {i+1} Score: {score} points")
            input("\nPress Enter to continue to next scenario...")
        
        # Final results
        print(f"\n{'='*50}")
        print("PRACTICE SESSION COMPLETE")
        print("=" * 30)
        print(f"Total Score: {total_score}/{max_score} ({total_score/max_score*100:.1f}%)")
        
        if total_score >= 50:
            grade = "Excellent! You're ready for live trading."
        elif total_score >= 35:
            grade = "Good! Continue practicing specific areas."
        elif total_score >= 20:
            grade = "Fair. Review fundamentals before live trading."
        else:
            grade = "Needs improvement. Study more before risking real money."
        
        print(f"Grade: {grade}")
        
        # Save results
        result = {
            "date": datetime.now().isoformat(),
            "total_score": total_score,
            "max_score": max_score,
            "percentage": total_score/max_score*100,
            "grade": grade
        }
        
        try:
            with open("practice_results.json", 'r') as f:
                results = json.load(f)
        except:
            results = []
        
        results.append(result)
        
        with open("practice_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Results saved to practice_results.json")

def main():
    practice = PracticeScenarios()
    practice.run_practice_session()

if __name__ == "__main__":
    main()