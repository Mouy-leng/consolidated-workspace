# Development Machine Setup Instructions

## Current System Status ✅

Your system already has these key components installed:
- **Cursor** (AI Code Editor) - Ready to use
- **Git** (v2.48.1.1) - Version control system
- **Node.js** (v22.16.0) - JavaScript runtime
- **Python** (v3.13) - Programming language
- **PowerShell 7** (v7.5.3) - Advanced shell

## 🚨 IMPORTANT: 2.5" SATA Drive Not Detected

The 2.5" SATA drive you mentioned is not currently detected by the system. Please:

1. **Physical Connection**: Ensure the drive is properly connected to:
   - SATA data cable → Motherboard
   - SATA power cable → Power supply

2. **BIOS/UEFI Check**: Boot into BIOS/UEFI and verify the drive appears in storage devices

3. **After Connection**: Run the setup script below to initialize the drive

## Setup Steps

### Step 1: Run Administrative Setup 🔧

**IMPORTANT**: Run PowerShell as Administrator, then execute:

```powershell
# Navigate to the script location
cd "C:\Users\lengk\GenX_FX_Remote"

# Run the main setup script
.\setup_dev_machine.ps1
```

This script will:
- ✅ Initialize and format your 2.5" SATA drive (when connected)
- ✅ Set proper permissions for all drives
- ✅ Create development directories (C:\Dev\Projects, C:\Dev\Tools, C:\Dev\Workspace)
- ✅ Enable Windows Developer Mode
- ✅ Configure user access for all users

### Step 2: Install Additional Development Tools 🛠️

```powershell
# Run the tools installation script
.\install_dev_tools.ps1
```

This will install:
- Visual Studio Code (if not present)
- Windows Terminal
- Docker Desktop
- Postman
- Useful VS Code extensions

### Step 3: Current Drive Configuration 💾

**Main System Drive (Disk 0 - 512GB Micron SSD):**
- `C:` - OS (248GB) - System drive with Windows
- `D:` - DATA (262GB) - Currently available for user data

**USB Drive (Disk 1 - 62GB):**
- `I:` - Dahua U156 - Removable storage

**Missing Drive:**
- Your 2.5" SATA drive - Not currently detected

### Step 4: User Access Configuration 👥

Current users with admin access:
- `lengk` (you)
- `Administrator`
- `USER`

After running the setup script, all users will have full control over:
- D: drive (DATA partition)
- Any new drives created
- Development directories under C:\Dev\

**Note**: System drive (C:) permissions are kept restrictive for security.

### Step 5: Development Environment Setup 🚀

Once setup is complete, you'll have:

```
C:\Dev\
├── Projects\     (Your development projects)
├── Tools\        (Development tools and utilities)
└── Workspace\    (Working directories for different projects)
```

### Step 6: SATA Drive Setup (When Connected) 🔌

After connecting your 2.5" SATA drive:

1. The setup script will automatically detect it
2. You'll be prompted to initialize and format it
3. It will be formatted as NTFS with label "DEVELOPMENT"
4. Full user permissions will be set automatically

**Drive Letter Assignment**: The system will auto-assign the next available drive letter (likely E:, F:, etc.)

## Safety Features 🛡️

- **System Drive Protection**: C: drive permissions remain unchanged
- **Confirmation Prompts**: All destructive operations require confirmation
- **Backup Reminder**: Always backup important data before drive operations

## Troubleshooting 🔍

### SATA Drive Not Detected:
1. Check physical connections (data + power cables)
2. Verify in BIOS/UEFI settings
3. Try a different SATA port
4. Test the drive on another computer

### Permission Issues:
- Run scripts as Administrator
- Check Windows UAC settings
- Verify user accounts have proper group membership

### Tool Installation Issues:
- Ensure internet connection
- Check Windows Defender/antivirus settings
- Run PowerShell as Administrator

## Next Steps After Setup ✨

1. **Test Your Setup**:
   ```powershell
   # Test Cursor
   cursor C:\Dev\Projects

   # Test Git
   git --version

   # Test Node.js
   node --version

   # Test Python
   python --version
   ```

2. **Create Your First Project**:
   ```powershell
   mkdir "C:\Dev\Projects\MyFirstProject"
   cd "C:\Dev\Projects\MyFirstProject"
   cursor .
   ```

3. **Configure Development Environment**:
   - Set up your preferred shell profile
   - Configure Git with your credentials
   - Install language-specific packages (npm, pip, etc.)

## Machine Capabilities Summary 🖥️

After full setup, your development machine will support:

- **Multiple Programming Languages**: Python, JavaScript, TypeScript, C++, PowerShell
- **AI-Assisted Development**: Cursor with AI capabilities
- **Version Control**: Git with configured aliases
- **Containerization**: Docker Desktop (optional)
- **API Testing**: Postman (optional)
- **Multiple User Access**: All users can access development resources
- **Flexible Storage**: Multiple drives available for different purposes

## Support 📞

If you encounter issues:
1. Check this document first
2. Verify all prerequisites are met
3. Run scripts with Administrator privileges
4. Check system logs for error details

---

**Remember**: Always connect and verify your 2.5" SATA drive before running the administrative setup script for complete configuration.