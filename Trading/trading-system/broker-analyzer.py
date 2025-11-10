#!/usr/bin/env python3
"""
Broker Analysis & Recommendation System
Analyzes brokers for trading system integration, deposits/withdrawals, security, and management
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

class BrokerAnalyzer:
    def __init__(self):
        self.current_broker = "FBS"
        self.current_balance = 47.79
        self.user_location = "Global"  # Update based on your location
        
        # Broker database with comprehensive analysis
        self.brokers = {
            "FBS": {
                "name": "FBS Markets Inc",
                "regulation": ["CySEC", "ASIC", "FSCA"],
                "min_deposit": 100,
                "spreads": {"EURUSD": 0.0, "XAUUSD": 0.35},
                "deposit_methods": ["Card", "Bank Wire", "Skrill", "Neteller", "Crypto"],
                "withdrawal_time": "1-3 days",
                "platforms": ["MT4", "MT5", "FBS Trader"],
                "copy_trading": True,
                "api_support": True,
                "project_tools": ["Portfolio Manager", "Economic Calendar", "Trading Signals"],
                "security": {"2FA": True, "SSL": True, "Segregated_Funds": True},
                "location": "Cyprus, Australia, South Africa",
                "pros": ["No spread on major pairs", "Good for small accounts", "Multiple platforms"],
                "cons": ["Limited research tools", "Customer service varies"],
                "rating": 7.5,
                "best_for": "Beginners, Small accounts, Automated trading"
            },
            
            "IC_Markets": {
                "name": "IC Markets",
                "regulation": ["ASIC", "CySEC", "FSA"],
                "min_deposit": 200,
                "spreads": {"EURUSD": 0.1, "XAUUSD": 0.13},
                "deposit_methods": ["Card", "Bank Wire", "Skrill", "Neteller", "PayPal"],
                "withdrawal_time": "1-2 days",
                "platforms": ["MT4", "MT5", "cTrader"],
                "copy_trading": True,
                "api_support": True,
                "project_tools": ["Advanced Analytics", "Trading Central", "AutoChartist"],
                "security": {"2FA": True, "SSL": True, "Segregated_Funds": True},
                "location": "Australia, Cyprus, Seychelles",
                "pros": ["Raw spreads", "Fast execution", "Professional tools"],
                "cons": ["Higher minimum deposit", "Commission-based"],
                "rating": 8.5,
                "best_for": "Professional traders, Scalping, API trading"
            },
            
            "XM": {
                "name": "Trading Point Holdings Ltd",
                "regulation": ["CySEC", "ASIC", "IFSC"],
                "min_deposit": 5,
                "spreads": {"EURUSD": 1.0, "XAUUSD": 0.35},
                "deposit_methods": ["Card", "Bank Wire", "Skrill", "Neteller", "Local methods"],
                "withdrawal_time": "1-2 days",
                "platforms": ["MT4", "MT5"],
                "copy_trading": True,
                "api_support": True,
                "project_tools": ["Economic Calendar", "Trading Signals", "Market Research"],
                "security": {"2FA": True, "SSL": True, "Segregated_Funds": True},
                "location": "Cyprus, Australia, Belize",
                "pros": ["Very low minimum deposit", "Good education", "Multiple bonuses"],
                "cons": ["Wider spreads", "Limited advanced tools"],
                "rating": 7.8,
                "best_for": "Beginners, Micro accounts, Learning"
            },
            
            "Pepperstone": {
                "name": "Pepperstone Limited",
                "regulation": ["ASIC", "FCA", "CySEC", "SCB"],
                "min_deposit": 200,
                "spreads": {"EURUSD": 0.09, "XAUUSD": 0.22},
                "deposit_methods": ["Card", "Bank Wire", "PayPal", "Skrill", "Neteller"],
                "withdrawal_time": "1-2 days",
                "platforms": ["MT4", "MT5", "cTrader", "TradingView"],
                "copy_trading": True,
                "api_support": True,
                "project_tools": ["TradingView Charts", "AutoChartist", "Trading Central"],
                "security": {"2FA": True, "SSL": True, "Segregated_Funds": True},
                "location": "Australia, UK, Cyprus, Bahamas",
                "pros": ["TradingView integration", "Fast execution", "Multiple regulators"],
                "cons": ["Higher minimum deposit", "No crypto trading"],
                "rating": 8.7,
                "best_for": "Professional traders, Chart analysis, Multiple platforms"
            },
            
            "FTMO": {
                "name": "FTMO (Prop Trading)",
                "regulation": ["Proprietary Trading Firm"],
                "min_deposit": 0,  # Evaluation fee applies
                "spreads": {"EURUSD": 0.0, "XAUUSD": 0.2},
                "deposit_methods": ["Card", "Bank Wire", "Crypto"],
                "withdrawal_time": "1-3 days",
                "platforms": ["MT4", "MT5", "DXTrade"],
                "copy_trading": False,
                "api_support": True,
                "project_tools": ["Performance Analytics", "Risk Management", "Trading Psychology"],
                "security": {"2FA": True, "SSL": True, "Segregated_Funds": True},
                "location": "Czech Republic",
                "pros": ["Funded accounts up to $400k", "Keep 80-90% profits", "No personal risk"],
                "cons": ["Must pass evaluation", "Strict rules", "Monthly fees"],
                "rating": 8.9,
                "best_for": "Profitable traders, Scaling capital, Professional trading"
            },
            
            "Interactive_Brokers": {
                "name": "Interactive Brokers LLC",
                "regulation": ["SEC", "FINRA", "FCA", "IIROC"],
                "min_deposit": 0,
                "spreads": {"EURUSD": 0.1, "XAUUSD": 0.25},
                "deposit_methods": ["Bank Wire", "ACH", "Check"],
                "withdrawal_time": "1-3 days",
                "platforms": ["TWS", "IBKR Mobile", "API"],
                "copy_trading": False,
                "api_support": True,
                "project_tools": ["Portfolio Analyst", "Risk Navigator", "Algo Trading"],
                "security": {"2FA": True, "SSL": True, "SIPC_Protected": True},
                "location": "United States, UK, Canada, Australia",
                "pros": ["Institutional-grade", "Low costs", "Global markets", "Advanced tools"],
                "cons": ["Complex platform", "Monthly fees", "High learning curve"],
                "rating": 9.2,
                "best_for": "Professional traders, Institutional trading, Multi-asset portfolios"
            },
            
            "Binance": {
                "name": "Binance (Crypto Trading)",
                "regulation": ["Various regional licenses"],
                "min_deposit": 10,
                "spreads": {"BTCUSDT": 0.1, "ETHUSDT": 0.1},
                "deposit_methods": ["Crypto", "Card", "Bank Transfer", "P2P"],
                "withdrawal_time": "Minutes to hours",
                "platforms": ["Binance App", "Binance Web", "API"],
                "copy_trading": True,
                "api_support": True,
                "project_tools": ["Trading Bot", "Portfolio Management", "Futures Calculator"],
                "security": {"2FA": True, "SSL": True, "SAFU_Fund": True},
                "location": "Global (Various jurisdictions)",
                "pros": ["Largest crypto exchange", "Low fees", "Many trading pairs", "DeFi access"],
                "cons": ["Crypto only", "Regulatory uncertainties", "Complex for beginners"],
                "rating": 8.3,
                "best_for": "Crypto trading, DeFi, High-frequency trading"
            }
        }
        
    def analyze_current_situation(self):
        """Analyze current FBS situation"""
        current = self.brokers["FBS"]
        
        analysis = {
            "current_broker": "FBS",
            "current_balance": self.current_balance,
            "current_performance": {
                "account_size": "Micro account",
                "suitable_for_automation": True,
                "growth_potential": "Limited by small balance",
                "risk_level": "Conservative (1.5% per trade)"
            },
            "current_limitations": [
                "Small account balance ($47.79)",
                "Limited research tools",
                "Basic project management features",
                "Standard customer service"
            ],
            "current_advantages": [
                "Good for small accounts",
                "MT4/MT5 automation support",
                "No spread on major pairs",
                "Multiple deposit methods"
            ]
        }
        
        return analysis
    
    def calculate_broker_score(self, broker_data: Dict, user_criteria: Dict) -> float:
        """Calculate broker score based on user criteria"""
        score = 0.0
        max_score = 0.0
        
        # Weights for different criteria
        weights = {
            "min_deposit": user_criteria.get("deposit_weight", 0.2),
            "spreads": user_criteria.get("spread_weight", 0.2),
            "withdrawal_speed": user_criteria.get("withdrawal_weight", 0.15),
            "regulation": user_criteria.get("security_weight", 0.15),
            "project_tools": user_criteria.get("tools_weight", 0.15),
            "platforms": user_criteria.get("platform_weight", 0.1),
            "overall_rating": user_criteria.get("rating_weight", 0.05)
        }
        
        # Score minimum deposit (lower is better for small accounts)
        if broker_data["min_deposit"] <= self.current_balance:
            score += weights["min_deposit"] * 10
        elif broker_data["min_deposit"] <= 200:
            score += weights["min_deposit"] * 7
        else:
            score += weights["min_deposit"] * 3
        max_score += weights["min_deposit"] * 10
        
        # Score spreads (lower is better)
        avg_spread = sum(broker_data["spreads"].values()) / len(broker_data["spreads"])
        if avg_spread <= 0.1:
            score += weights["spreads"] * 10
        elif avg_spread <= 0.5:
            score += weights["spreads"] * 7
        else:
            score += weights["spreads"] * 5
        max_score += weights["spreads"] * 10
        
        # Score withdrawal speed
        if "1" in broker_data["withdrawal_time"]:
            score += weights["withdrawal_speed"] * 10
        elif "2" in broker_data["withdrawal_time"]:
            score += weights["withdrawal_speed"] * 8
        else:
            score += weights["withdrawal_speed"] * 6
        max_score += weights["withdrawal_speed"] * 10
        
        # Score regulation
        score += weights["regulation"] * min(len(broker_data["regulation"]) * 3, 10)
        max_score += weights["regulation"] * 10
        
        # Score project tools
        score += weights["project_tools"] * min(len(broker_data["project_tools"]) * 3, 10)
        max_score += weights["project_tools"] * 10
        
        # Score platforms
        score += weights["platforms"] * min(len(broker_data["platforms"]) * 2.5, 10)
        max_score += weights["platforms"] * 10
        
        # Score overall rating
        score += weights["overall_rating"] * broker_data["rating"]
        max_score += weights["overall_rating"] * 10
        
        return (score / max_score) * 100
    
    def recommend_brokers(self, user_criteria: Dict = None) -> List[Dict]:
        """Recommend brokers based on user criteria"""
        
        # Default criteria for current situation
        if user_criteria is None:
            user_criteria = {
                "deposit_weight": 0.25,    # Important for small account
                "spread_weight": 0.20,     # Important for profitability
                "withdrawal_weight": 0.20, # Important for easy access
                "security_weight": 0.15,   # Important for safety
                "tools_weight": 0.15,      # Important for project management
                "platform_weight": 0.05    # Less important (already using MT4/MT5)
            }
        
        recommendations = []
        
        for broker_id, broker_data in self.brokers.items():
            score = self.calculate_broker_score(broker_data, user_criteria)
            
            recommendation = {
                "broker_id": broker_id,
                "name": broker_data["name"],
                "score": round(score, 1),
                "rating": broker_data["rating"],
                "min_deposit": broker_data["min_deposit"],
                "suitable_for_current_balance": broker_data["min_deposit"] <= self.current_balance,
                "key_advantages": broker_data["pros"][:3],
                "key_disadvantages": broker_data["cons"][:2],
                "best_for": broker_data["best_for"],
                "deposit_methods": len(broker_data["deposit_methods"]),
                "withdrawal_time": broker_data["withdrawal_time"],
                "project_tools": broker_data["project_tools"]
            }
            
            recommendations.append(recommendation)
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def generate_migration_plan(self, target_broker: str) -> Dict:
        """Generate migration plan to new broker"""
        
        if target_broker not in self.brokers:
            return {"error": "Broker not found"}
        
        target = self.brokers[target_broker]
        
        plan = {
            "current_broker": "FBS",
            "target_broker": target_broker,
            "migration_steps": [],
            "timeline": "1-2 weeks",
            "requirements": [],
            "risks": [],
            "benefits": []
        }
        
        # Generate steps
        steps = [
            "1. Research and verify target broker regulation",
            "2. Open demo account for testing",
            "3. Test deposit methods and minimum amounts",
            "4. Verify trading platform compatibility",
            "5. Test API connectivity for automated trading",
            "6. Open live account with minimum deposit",
            "7. Test small trades and withdrawals",
            "8. Gradually migrate funds (if keeping both)",
            "9. Update trading system configuration",
            "10. Monitor performance for 1-2 weeks"
        ]
        
        plan["migration_steps"] = steps
        
        # Requirements
        if target["min_deposit"] > self.current_balance:
            plan["requirements"].append(f"Additional funding needed: ${target['min_deposit'] - self.current_balance}")
        
        plan["requirements"].extend([
            "Identity verification documents",
            "Proof of address",
            "Tax information (if required)",
            "Update trading system credentials"
        ])
        
        # Risks
        plan["risks"] = [
            "Platform learning curve",
            "Potential downtime during migration",
            "Different trading conditions",
            "Regulatory differences"
        ]
        
        # Benefits
        plan["benefits"] = target["pros"]
        
        return plan
    
    def save_analysis(self, analysis_data: Dict):
        """Save analysis to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"broker_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        return filename

def main():
    """Main analysis function"""
    analyzer = BrokerAnalyzer()
    
    print("🏦 BROKER ANALYSIS & RECOMMENDATION SYSTEM")
    print("=" * 60)
    print(f"📊 Current Broker: FBS | Balance: ${analyzer.current_balance}")
    print("")
    
    # Analyze current situation
    print("🔍 ANALYZING CURRENT SITUATION...")
    current_analysis = analyzer.analyze_current_situation()
    
    print(f"✅ Current Performance: {current_analysis['current_performance']['account_size']}")
    print(f"🤖 Automation Ready: {current_analysis['current_performance']['suitable_for_automation']}")
    print("")
    
    # Get recommendations
    print("🎯 GENERATING BROKER RECOMMENDATIONS...")
    recommendations = analyzer.recommend_brokers()
    
    print(f"\n📋 TOP BROKER RECOMMENDATIONS:")
    print("-" * 50)
    
    for i, rec in enumerate(recommendations[:5], 1):
        suitable = "✅" if rec["suitable_for_current_balance"] else "⚠️"
        print(f"{i}. {rec['name']} - Score: {rec['score']}/100 {suitable}")
        print(f"   Min Deposit: ${rec['min_deposit']} | Rating: {rec['rating']}/10")
        print(f"   Best For: {rec['best_for']}")
        print(f"   Withdrawal: {rec['withdrawal_time']}")
        print(f"   Tools: {', '.join(rec['project_tools'][:2])}")
        print("")
    
    # Generate migration plan for top recommendation
    top_broker = recommendations[0]["broker_id"]
    if top_broker != "FBS":
        print(f"📋 MIGRATION PLAN TO {recommendations[0]['name'].upper()}:")
        print("-" * 50)
        migration_plan = analyzer.generate_migration_plan(top_broker)
        
        print("🗓️ Timeline:", migration_plan["timeline"])
        print("\n📝 Key Steps:")
        for step in migration_plan["migration_steps"][:5]:
            print(f"   {step}")
        print("   ...")
        
        print(f"\n💡 Benefits:")
        for benefit in migration_plan["benefits"][:3]:
            print(f"   ✅ {benefit}")
    
    # Save analysis
    full_analysis = {
        "timestamp": datetime.now().isoformat(),
        "current_analysis": current_analysis,
        "recommendations": recommendations,
        "migration_plan": analyzer.generate_migration_plan(recommendations[0]["broker_id"]) if recommendations[0]["broker_id"] != "FBS" else None
    }
    
    filename = analyzer.save_analysis(full_analysis)
    print(f"\n💾 Full analysis saved to: {filename}")
    
    return recommendations

if __name__ == "__main__":
    recommendations = main()