#!/usr/bin/env python3
"""
Payment Link Organizer and Connection Manager
Organizes payment links and creates proper connections
"""

import json
import re
from datetime import datetime
from typing import Dict, List

class LinkOrganizer:
    def __init__(self):
        self.categories = {
            'trading_tools': ['trading', 'mt5', 'forex', 'signals', 'bot'],
            'courses': ['course', 'training', 'education', 'learn'],
            'software': ['software', 'app', 'tool', 'plugin'],
            'subscriptions': ['subscription', 'monthly', 'premium', 'pro'],
            'one_time': ['buy', 'purchase', 'download', 'access']
        }
    
    def categorize_links(self, payment_links):
        """Categorize payment links based on context"""
        categorized = {
            'trading_tools': [],
            'courses': [],
            'software': [],
            'subscriptions': [],
            'one_time': [],
            'uncategorized': []
        }
        
        for link in payment_links:
            category = self.determine_category(link)
            categorized[category].append(link)
        
        return categorized
    
    def determine_category(self, link):
        """Determine category based on file name and context"""
        text = f"{link['file_name']} {link.get('url', '')}".lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'uncategorized'
    
    def create_connection_map(self, categorized_links):
        """Create connections between related payment links"""
        connections = {}
        
        for category, links in categorized_links.items():
            if len(links) > 1:
                connections[category] = self.find_related_links(links)
        
        return connections
    
    def find_related_links(self, links):
        """Find related links within a category"""
        related = []
        
        for i, link1 in enumerate(links):
            for j, link2 in enumerate(links[i+1:], i+1):
                similarity = self.calculate_similarity(link1, link2)
                if similarity > 0.3:  # 30% similarity threshold
                    related.append({
                        'link1': link1['url'],
                        'link2': link2['url'],
                        'similarity': similarity,
                        'reason': self.get_similarity_reason(link1, link2)
                    })
        
        return related
    
    def calculate_similarity(self, link1, link2):
        """Calculate similarity between two links"""
        # Simple similarity based on file names and providers
        name_similarity = self.text_similarity(link1['file_name'], link2['file_name'])
        provider_match = 1.0 if link1['payment_provider'] == link2['payment_provider'] else 0.0
        
        return (name_similarity * 0.7) + (provider_match * 0.3)
    
    def text_similarity(self, text1, text2):
        """Calculate text similarity using simple word matching"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_similarity_reason(self, link1, link2):
        """Get reason for similarity between links"""
        reasons = []
        
        if link1['payment_provider'] == link2['payment_provider']:
            reasons.append(f"Same provider ({link1['payment_provider']})")
        
        if self.text_similarity(link1['file_name'], link2['file_name']) > 0.5:
            reasons.append("Similar file names")
        
        return ", ".join(reasons) if reasons else "General similarity"
    
    def generate_organized_structure(self, categorized_links, connections):
        """Generate organized structure with proper connections"""
        structure = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_categories': len([cat for cat, links in categorized_links.items() if links]),
                'total_links': sum(len(links) for links in categorized_links.values())
            },
            'categories': {},
            'connections': connections,
            'recommendations': self.generate_recommendations(categorized_links)
        }
        
        for category, links in categorized_links.items():
            if links:
                structure['categories'][category] = {
                    'count': len(links),
                    'links': links,
                    'providers': list(set(link['payment_provider'] for link in links))
                }
        
        return structure
    
    def generate_recommendations(self, categorized_links):
        """Generate recommendations for link organization"""
        recommendations = []
        
        # Check for duplicate providers
        all_links = []
        for links in categorized_links.values():
            all_links.extend(links)
        
        provider_counts = {}
        for link in all_links:
            provider = link['payment_provider']
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        for provider, count in provider_counts.items():
            if count > 3:
                recommendations.append({
                    'type': 'consolidation',
                    'message': f"Consider consolidating {count} {provider} links",
                    'priority': 'medium'
                })
        
        # Check for missing categories
        if not categorized_links['trading_tools']:
            recommendations.append({
                'type': 'missing_category',
                'message': "No trading tools payment links found",
                'priority': 'low'
            })
        
        return recommendations

def main():
    organizer = LinkOrganizer()
    
    # Load payment links from scanner output
    try:
        # Find the most recent payment links file
        import glob
        files = glob.glob("payment_links_*.json")
        if not files:
            print("❌ No payment links file found. Run the scanner first.")
            return
        
        latest_file = max(files)
        print(f"📂 Loading payment links from {latest_file}")
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Extract all links
        all_links = []
        for provider_links in data['by_provider'].values():
            all_links.extend(provider_links)
        
        print(f"🔗 Processing {len(all_links)} payment links")
        
        # Categorize links
        categorized = organizer.categorize_links(all_links)
        
        # Create connections
        connections = organizer.create_connection_map(categorized)
        
        # Generate organized structure
        organized_structure = organizer.generate_organized_structure(categorized, connections)
        
        # Save organized structure
        output_file = f"organized_payment_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(organized_structure, f, indent=2)
        
        print(f"💾 Organized structure saved to {output_file}")
        
        # Display summary
        print("\n📊 ORGANIZATION SUMMARY:")
        print("=" * 30)
        
        for category, data in organized_structure['categories'].items():
            print(f"{category.replace('_', ' ').title()}: {data['count']} links")
            print(f"  Providers: {', '.join(data['providers'])}")
        
        if organized_structure['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in organized_structure['recommendations']:
                print(f"  • {rec['message']} (Priority: {rec['priority']})")
        
        print(f"\n✅ Organization completed!")
        
    except Exception as e:
        print(f"❌ Error organizing links: {e}")

if __name__ == "__main__":
    main()