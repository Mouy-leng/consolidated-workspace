import os

# Set all environment variables from provided credentials
os.environ['GITHUB_TOKEN'] = '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'
os.environ['GITLAB_TOKEN'] = 'glpat-3p76i6YP3Iwiu25bO2QtAm86MQp1OmhsNjlpCw.01.121l499kx'
os.environ['CURSOR_CLI_API_KEY'] = 'key_03096e697424c5489927db265b35a7ab045502673326d9bf1deb31ee3bfbf80f'
os.environ['AMP_TOKEN'] = 'sgamp_user_01K1XBP8C5SZXYP88QD166AX1W_72c12a40546c130db17817dc9c92cb3770ecbe93e34a9fd23c8e9a2daa8e942c'

# Update .env file with all credentials
env_content = f"""
GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}
GITLAB_TOKEN={os.environ['GITLAB_TOKEN']}
CURSOR_CLI_API_KEY={os.environ['CURSOR_CLI_API_KEY']}
AMP_TOKEN={os.environ['AMP_TOKEN']}
BYBIT_API_KEY=your_bybit_key
BYBIT_SECRET=your_bybit_secret
FXCM_USERNAME=your_fxcm_username
FXCM_PASSWORD=your_fxcm_password
GEMINI_API_KEY=your_gemini_key
TELEGRAM_BOT_TOKEN=your_telegram_token
DISCORD_BOT_TOKEN=your_discord_token
"""

with open('.env', 'w') as f:
    f.write(env_content.strip())

print("All credentials configured in .env file")
print("GitHub profile setup ready")