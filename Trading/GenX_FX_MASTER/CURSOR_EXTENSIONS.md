# Recommended Cursor Extensions for GenX_FX

## Essential Extensions

### Python Development
- **Python** (ms-python.python) - Core Python support
- **Python Debugger** (ms-python.debugpy) - Enhanced debugging
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **autopep8** (ms-python.autopep8) - PEP 8 formatting
- **Pylance** (ms-python.vscode-pylance) - Advanced Python language support

### AI & Development
- **Cursor Tab** (Built-in) - AI code completion
- **Cursor Chat** (Built-in) - AI chat assistance
- **GitHub Copilot** (github.copilot) - AI pair programming
- **GitHub Copilot Chat** (github.copilot-chat) - Enhanced AI chat

### Git & Version Control
- **GitLens** (eamodio.gitlens) - Enhanced Git capabilities
- **Git History** (donjayamanne.githistory) - Git history viewer
- **Git Graph** (mhutchie.git-graph) - Visual git graph

### Code Quality
- **SonarLint** (sonarsource.sonarlint-vscode) - Code quality analysis
- **Error Lens** (usernamehw.errorlens) - Inline error highlighting
- **TODO Highlight** (wayou.vscode-todo-highlight) - Highlight TODO comments

### Web Development (if using web interface)
- **ES7+ React/Redux/React-Native snippets** - React development
- **Prettier** (esbenp.prettier-vscode) - Code formatter
- **Live Server** (ritwickdey.liveserver) - Local development server
- **Auto Rename Tag** (formulahendry.auto-rename-tag) - HTML tag management

### Database
- **SQLite Viewer** (qwtel.sqlite-viewer) - SQLite database viewer
- **PostgreSQL** (ckolkman.vscode-postgres) - PostgreSQL support
- **Database Client** (cweijan.vscode-mysql-client2) - Multi-database client

### JSON & Data
- **JSON Tools** (eriklynd.json-tools) - JSON utilities
- **CSV Viewer** (grapecity.gc-excelviewer) - CSV file viewer
- **YAML** (redhat.vscode-yaml) - YAML support

### Docker & Containers
- **Docker** (ms-azuretools.vscode-docker) - Docker support
- **Remote-Containers** (ms-vscode-remote.remote-containers) - Container development

### Markdown & Documentation
- **Markdown All in One** (yzhang.markdown-all-in-one) - Markdown support
- **Markdown Preview Enhanced** (shd101wyy.markdown-preview-enhanced) - Enhanced preview

### Theme & UI
- **Material Icon Theme** (pkief.material-icon-theme) - File icons
- **One Dark Pro** (zhuangtongfa.material-theme) - Dark theme
- **Bracket Pair Colorizer** (coenraads.bracket-pair-colorizer) - Colorized brackets

### Productivity
- **Path Intellisense** (christian-kohler.path-intellisense) - Path autocompletion
- **Auto Import** (steoates.autoimport) - Automatic imports
- **IntelliCode** (visualstudioexptteam.vscodeintellicode) - AI-assisted development
- **Thunder Client** (rangav.vscode-thunder-client) - REST API client

## Installation Instructions

### Method 1: Through Cursor Interface
1. Open Cursor
2. Click on the Extensions icon (⬜) in the left sidebar
3. Search for each extension by name
4. Click "Install" for each extension

### Method 2: Command Palette
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Extensions: Install Extensions"
3. Search and install each extension

## Extension Configuration

### Python Extension Settings
Add these to your Cursor settings:
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

### GitLens Settings
```json
{
    "gitlens.currentLine.enabled": false,
    "gitlens.hovers.currentLine.over": "line",
    "gitlens.codeLens.authors.enabled": true,
    "gitlens.codeLens.recentChange.enabled": true
}
```

### Prettier Configuration
```json
{
    "prettier.singleQuote": false,
    "prettier.trailingComma": "es5",
    "prettier.tabWidth": 2,
    "prettier.semi": true
}
```

## AI Features Configuration

### Cursor-Specific Settings
```json
{
    "cursor.general.enableCursorTab": true,
    "cursor.chat.enableChatView": true,
    "cursor.autocomplete.enabled": true,
    "cursor.autocomplete.suggestOnEveryKeystroke": true
}
```

## Trading System Specific Extensions

### Financial Data
- Consider extensions for handling CSV/Excel files for market data
- JSON viewers for API responses
- REST clients for testing trading APIs

### Monitoring
- Log file viewers for trading system logs
- Dashboard extensions for monitoring trading performance

## Notes
- Some extensions may require additional configuration
- Check extension documentation for specific setup instructions
- Update extensions regularly for latest features and security patches
- Disable unused extensions to improve performance