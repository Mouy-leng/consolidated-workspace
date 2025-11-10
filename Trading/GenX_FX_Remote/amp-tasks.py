# AMP Task 2: Upload secrets to GitHub
import requests
import os

GITHUB_TOKEN = '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'
REPO = 'Mouy-leng/GenX_FX'

secrets = {
    'BYBIT_API_KEY': 'your_bybit_key',
    'BYBIT_SECRET': 'your_bybit_secret', 
    'FXCM_USERNAME': 'your_fxcm_username',
    'FXCM_PASSWORD': 'your_fxcm_password',
    'GEMINI_API_KEY': 'your_gemini_key',
    'TELEGRAM_BOT_TOKEN': 'your_telegram_token'
}

print("AMP: Upload secrets to GitHub repository")
print("Run: python github-secrets-api.py")