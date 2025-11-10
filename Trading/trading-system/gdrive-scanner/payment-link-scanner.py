#!/usr/bin/env python3
"""
Google Drive Payment Link Scanner
Scans Google Drive for payment links and organizes them
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class PaymentLinkScanner:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.service = None
        self.payment_patterns = [
            r'https://buy\.stripe\.com/[a-zA-Z0-9]+',
            r'https://checkout\.stripe\.com/[a-zA-Z0-9/]+',
            r'https://paypal\.me/[a-zA-Z0-9]+',
            r'https://www\.paypal\.com/paypalme/[a-zA-Z0-9]+',
            r'https://gumroad\.com/l/[a-zA-Z0-9]+',
            r'https://[a-zA-Z0-9-]+\.gumroad\.com/l/[a-zA-Z0-9]+',
            r'https://lemonsqueezy\.com/checkout/buy/[a-zA-Z0-9-]+',
            r'https://paddle\.com/checkout/[a-zA-Z0-9-]+',
            r'https://buy\.paddle\.com/product/[a-zA-Z0-9]+',
        ]
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        token_file = 'token.json'
        
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Google Drive authenticated")
    
    def scan_files(self, folder_id=None):
        """Scan Google Drive files for payment links"""
        if not self.service:
            self.authenticate()
        
        payment_links = []
        
        try:
            query = "mimeType='application/vnd.google-apps.document' or mimeType='text/plain' or mimeType='application/pdf'"
            if folder_id:
                query += f" and parents in '{folder_id}'"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            for file in files:
                print(f"🔍 Scanning: {file['name']}")
                links = self.extract_payment_links_from_file(file)
                if links:
                    payment_links.extend(links)
            
        except Exception as e:
            print(f"❌ Error scanning files: {e}")
        
        return payment_links
    
    def extract_payment_links_from_file(self, file_info):
        """Extract payment links from a specific file"""
        links = []
        
        try:
            file_id = file_info['id']
            
            # Export Google Docs as plain text
            if file_info['mimeType'] == 'application/vnd.google-apps.document':
                content = self.service.files().export(
                    fileId=file_id, 
                    mimeType='text/plain'
                ).execute().decode('utf-8')
            else:
                # For other file types, get content if possible
                content = self.service.files().get_media(fileId=file_id).execute().decode('utf-8')
            
            # Search for payment links
            for pattern in self.payment_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    links.append({
                        'url': match,
                        'file_name': file_info['name'],
                        'file_id': file_info['id'],
                        'file_link': file_info['webViewLink'],
                        'modified_time': file_info['modifiedTime'],
                        'payment_provider': self.identify_provider(match),
                        'found_at': datetime.now().isoformat()
                    })
        
        except Exception as e:
            print(f"⚠️  Could not scan {file_info['name']}: {e}")
        
        return links
    
    def identify_provider(self, url):
        """Identify payment provider from URL"""
        if 'stripe.com' in url:
            return 'Stripe'
        elif 'paypal' in url:
            return 'PayPal'
        elif 'gumroad.com' in url:
            return 'Gumroad'
        elif 'lemonsqueezy.com' in url:
            return 'Lemon Squeezy'
        elif 'paddle.com' in url:
            return 'Paddle'
        else:
            return 'Unknown'
    
    def organize_links(self, payment_links):
        """Organize payment links by provider and type"""
        organized = {
            'by_provider': {},
            'by_file': {},
            'summary': {
                'total_links': len(payment_links),
                'providers': set(),
                'files_with_links': set()
            }
        }
        
        for link in payment_links:
            provider = link['payment_provider']
            file_name = link['file_name']
            
            # Organize by provider
            if provider not in organized['by_provider']:
                organized['by_provider'][provider] = []
            organized['by_provider'][provider].append(link)
            
            # Organize by file
            if file_name not in organized['by_file']:
                organized['by_file'][file_name] = []
            organized['by_file'][file_name].append(link)
            
            # Update summary
            organized['summary']['providers'].add(provider)
            organized['summary']['files_with_links'].add(file_name)
        
        # Convert sets to lists for JSON serialization
        organized['summary']['providers'] = list(organized['summary']['providers'])
        organized['summary']['files_with_links'] = list(organized['summary']['files_with_links'])
        
        return organized
    
    def save_results(self, organized_links):
        """Save organized links to JSON file"""
        output_file = f"payment_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(organized_links, f, indent=2)
        
        print(f"💾 Results saved to {output_file}")
        return output_file
    
    def generate_report(self, organized_links):
        """Generate a readable report"""
        report = f"""
📊 PAYMENT LINKS SCAN REPORT
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 SUMMARY:
- Total Links Found: {organized_links['summary']['total_links']}
- Payment Providers: {len(organized_links['summary']['providers'])}
- Files with Links: {len(organized_links['summary']['files_with_links'])}

💳 BY PROVIDER:
"""
        
        for provider, links in organized_links['by_provider'].items():
            report += f"\n{provider}: {len(links)} links\n"
            for link in links[:3]:  # Show first 3 links
                report += f"  • {link['url']}\n"
            if len(links) > 3:
                report += f"  ... and {len(links) - 3} more\n"
        
        report += f"\n📁 BY FILE:\n"
        for file_name, links in organized_links['by_file'].items():
            report += f"\n{file_name}: {len(links)} links\n"
        
        return report

def main():
    scanner = PaymentLinkScanner()
    
    print("🔍 Starting Google Drive Payment Link Scanner")
    print("=" * 50)
    
    # Scan for payment links
    payment_links = scanner.scan_files()
    
    if not payment_links:
        print("❌ No payment links found")
        return
    
    print(f"✅ Found {len(payment_links)} payment links")
    
    # Organize links
    organized = scanner.organize_links(payment_links)
    
    # Save results
    output_file = scanner.save_results(organized)
    
    # Generate and display report
    report = scanner.generate_report(organized)
    print(report)
    
    # Save report
    report_file = f"payment_links_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to {report_file}")

if __name__ == "__main__":
    main()