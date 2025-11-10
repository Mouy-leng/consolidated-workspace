# Google Drive Payment Link Scanner

Automatically scans your Google Drive for payment links and organizes them properly.

## 🚀 Quick Start

1. **Setup Google Drive API:**
   ```bash
   python setup-gdrive-auth.py
   ```

2. **Run Complete Scanner:**
   ```powershell
   .\run-scanner.ps1
   ```

## 📋 Manual Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Google Drive API

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json`
6. Place in this directory

### 3. Run Scanner
```bash
python payment-link-scanner.py
```

### 4. Organize Links
```bash
python link-organizer.py
```

## 🔍 What It Finds

**Payment Providers Supported:**
- Stripe (buy.stripe.com, checkout.stripe.com)
- PayPal (paypal.me, paypalme)
- Gumroad (gumroad.com/l/)
- Lemon Squeezy (lemonsqueezy.com/checkout)
- Paddle (paddle.com/checkout, buy.paddle.com)

**File Types Scanned:**
- Google Docs
- Text files
- PDF files

## 📊 Output Files

- `payment_links_YYYYMMDD_HHMMSS.json` - Raw scan results
- `organized_payment_links_YYYYMMDD_HHMMSS.json` - Organized structure
- `payment_links_report_YYYYMMDD_HHMMSS.txt` - Human-readable report

## 🏷️ Categories

Links are automatically categorized into:
- **Trading Tools** - MT5, forex, signals, bots
- **Courses** - Training, education, learning
- **Software** - Apps, tools, plugins
- **Subscriptions** - Monthly, premium, pro
- **One-time** - Buy, purchase, download

## 🔗 Connections

The system identifies related links based on:
- Same payment provider
- Similar file names
- Content similarity
- Category matching

## 💡 Recommendations

Automatically generates recommendations for:
- Link consolidation
- Missing categories
- Duplicate providers
- Organization improvements

## 🔐 Security

- Uses OAuth 2.0 for Google Drive access
- Read-only permissions
- Local credential storage
- No data uploaded to external services