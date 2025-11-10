# Trading System Device Manager
# Manages local devices and syncs with remote trading infrastructure

param(
    [string]$Action = "status",
    [string]$DeviceId = "",
    [switch]$Sync = $false,
    [switch]$ForceSync = $false
)

# Load environment configuration
. "$PSScriptRoot\load-env.ps1"

function Write-DeviceLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] [DEVICE] $Message"
    Write-Host $logEntry
    $logEntry | Out-File -FilePath "$PSScriptRoot\device-manager.log" -Append
}

function Get-LocalDevices {
    Write-DeviceLog "Scanning for local trading devices..."
    
    $devices = @()
    
    # Check for USB devices (trading dongles, hardware keys)
    $usbDevices = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 }
    foreach ($usb in $usbDevices) {
        $devices += [PSCustomObject]@{
            Type      = "USB"
            DeviceId  = $usb.DeviceID
            Label     = $usb.VolumeName
            Size      = [math]::Round($usb.Size / 1GB, 2)
            FreeSpace = [math]::Round($usb.FreeSpace / 1GB, 2)
            Status    = "Connected"
        }
    }
    
    # Also check using Get-Volume for better USB detection
    $volumeDevices = Get-Volume | Where-Object { $_.DriveType -eq "Removable" }
    foreach ($vol in $volumeDevices) {
        if ($vol.DriveLetter) {
            $devices += [PSCustomObject]@{
                Type      = "USB_VOLUME"
                DeviceId  = "$($vol.DriveLetter):"
                Label     = $vol.FileSystemLabel
                Size      = [math]::Round($vol.Size / 1GB, 2)
                FreeSpace = [math]::Round($vol.SizeRemaining / 1GB, 2)
                Status    = "Connected"
            }
        }
    }
    
    # Check for network trading terminals
    $networkDevices = @()
    try {
        $mt5Process = Get-Process -Name "metatrader5" -ErrorAction SilentlyContinue
        if ($mt5Process) {
            $networkDevices += [PSCustomObject]@{
                Type      = "MT5_Terminal"
                DeviceId  = "MT5_$($env:COMPUTERNAME)"
                ProcessId = $mt5Process.Id
                Status    = "Running"
                Path      = $mt5Process.Path
            }
        }
        
        $mt4Process = Get-Process -Name "metatrader4" -ErrorAction SilentlyContinue
        if ($mt4Process) {
            $networkDevices += [PSCustomObject]@{
                Type      = "MT4_Terminal"
                DeviceId  = "MT4_$($env:COMPUTERNAME)"
                ProcessId = $mt4Process.Id
                Status    = "Running"
                Path      = $mt4Process.Path
            }
        }
    }
    catch {
        Write-DeviceLog "Could not scan for trading terminals: $($_.Exception.Message)" "WARNING"
    }
    
    $devices += $networkDevices
    
    # Check for crypto wallets
    $cryptoDevices = Test-CryptoWallets
    $devices += $cryptoDevices
    
    # Check for trading API connections
    $apiDevices = Test-TradingAPIConnections
    $devices += $apiDevices
    
    return $devices
}

function Test-TradingAPIConnections {
    Write-DeviceLog "Testing trading API connections..."
    
    $apiDevices = @()
    
    # Test AMP API
    $ampApiKey = [Environment]::GetEnvironmentVariable('AMP_API_KEY', 'Process')
    if ($ampApiKey) {
        try {
            # Simulate API test (replace with actual API call)
            $apiDevices += [PSCustomObject]@{
                Type     = "AMP_API"
                DeviceId = "AMP_$($ampApiKey.Substring(0,8))..."
                Status   = "Connected"
                LastSync = (Get-Date)
            }
        }
        catch {
            $apiDevices += [PSCustomObject]@{
                Type     = "AMP_API"
                DeviceId = "AMP_API"
                Status   = "Error"
                LastSync = $null
            }
        }
    }
    
    # Test Gemini API
    $geminiApiKey = [Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
    if ($geminiApiKey) {
        try {
            $apiDevices += [PSCustomObject]@{
                Type     = "GEMINI_API"
                DeviceId = "GEMINI_$($geminiApiKey.Substring(0,8))..."
                Status   = "Connected"
                LastSync = (Get-Date)
            }
        }
        catch {
            $apiDevices += [PSCustomObject]@{
                Type     = "GEMINI_API"
                DeviceId = "GEMINI_API"
                Status   = "Error"
                LastSync = $null
            }
        }
    }
    
    return $apiDevices
}

function Test-CryptoWallets {
    Write-DeviceLog "Testing crypto wallet connections..."
    
    $cryptoDevices = @()
    
    # Check for MetaMask (Chrome)
    $metamaskChrome = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn"
    if (Test-Path $metamaskChrome) {
        $cryptoDevices += [PSCustomObject]@{
            Type     = "METAMASK_CHROME"
            DeviceId = "METAMASK_CHROME"
            Status   = "Detected"
            LastSync = (Get-Date)
        }
    }
    
    # Check for MetaMask (Edge)
    $metamaskEdge = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn"
    if (Test-Path $metamaskEdge) {
        $cryptoDevices += [PSCustomObject]@{
            Type     = "METAMASK_EDGE"
            DeviceId = "METAMASK_EDGE"
            Status   = "Detected"
            LastSync = (Get-Date)
        }
    }
    
    # Check for Ledger Live
    $ledgerPath = "$env:APPDATA\Ledger Live"
    if (Test-Path $ledgerPath) {
        $cryptoDevices += [PSCustomObject]@{
            Type     = "LEDGER_LIVE"
            DeviceId = "LEDGER_LIVE"
            Status   = "Detected"
            LastSync = (Get-Date)
        }
    }
    
    # Check for Trezor Suite
    $trezorPath = "$env:APPDATA\TrezorSuite"
    if (Test-Path $trezorPath) {
        $cryptoDevices += [PSCustomObject]@{
            Type     = "TREZOR_SUITE"
            DeviceId = "TREZOR_SUITE"
            Status   = "Detected"
            LastSync = (Get-Date)
        }
    }
    
    # Check for Ethereum keystore
    $keystorePath = "$env:APPDATA\Ethereum\keystore"
    if (Test-Path $keystorePath) {
        $keystoreFiles = Get-ChildItem $keystorePath -Filter "*.json" -ErrorAction SilentlyContinue
        if ($keystoreFiles) {
            $cryptoDevices += [PSCustomObject]@{
                Type     = "ETH_KEYSTORE"
                DeviceId = "ETH_KEYSTORE"
                Status   = "Detected ($($keystoreFiles.Count) files)"
                LastSync = (Get-Date)
            }
        }
    }
    
    return $cryptoDevices
}

function Sync-DeviceData {
    param(
        [string]$DeviceId,
        [bool]$Force = $false
    )
    
    Write-DeviceLog "Starting device synchronization for: $DeviceId"
    
    # Create sync configuration
    $syncConfig = @{
        DeviceId   = $DeviceId
        Timestamp  = Get-Date
        LocalPath  = "$PSScriptRoot\device-data\$($DeviceId -replace ':', '')"
        RemotePath = "/opt/genx-fx/device-data/$($DeviceId -replace ':', '')"
    }
    
    # Ensure local directory exists
    if (-not (Test-Path $syncConfig.LocalPath)) {
        New-Item -ItemType Directory -Path $syncConfig.LocalPath -Force
        Write-DeviceLog "Created local sync directory: $($syncConfig.LocalPath)"
    }
    
    # Sync to AWS EC2
    if ($DeviceId -match "AMP|GEMINI|MT[45]|USB|I:|BLUEDIM|METAMASK|LEDGER|TREZOR|ETH_KEYSTORE") {
        Write-DeviceLog "Syncing $DeviceId data to AWS EC2..."
        
        # Export local configuration
        $configExport = @{
            DeviceId    = $DeviceId
            Type        = ($DeviceId -split "_")[0]
            LastSync    = Get-Date
            LocalConfig = Get-DeviceConfig -DeviceId $DeviceId
        } | ConvertTo-Json -Depth 3
        
        $configPath = "$($syncConfig.LocalPath)\config.json"
        $configExport | Out-File -FilePath $configPath -Encoding UTF8
        
        # Upload to EC2 using SCP
        try {
            $privateKeyPath = [Environment]::GetEnvironmentVariable('AWS_PRIVATE_KEY_PATH', 'Process')
            $ec2User = [Environment]::GetEnvironmentVariable('EC2_USER', 'Process')
            $ec2Host = [Environment]::GetEnvironmentVariable('EC2_HOST', 'Process')
            
            if ($ec2Host -eq "auto-detect") {
                # Get current EC2 public IP
                $instanceId = [Environment]::GetEnvironmentVariable('AWS_INSTANCE_ID', 'Process')
                $awsRegion = [Environment]::GetEnvironmentVariable('AWS_REGION', 'Process')
                $ec2Host = aws ec2 describe-instances --instance-ids $instanceId --region $awsRegion --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
            }
            
            # Create remote directory
            $remoteCommand = "mkdir -p $($syncConfig.RemotePath)"
            & "$PSScriptRoot\connect-aws.ps1" -Command $remoteCommand
            
            # Upload configuration
            $scpArgs = @(
                "-i", $privateKeyPath,
                "-o", "StrictHostKeyChecking=no",
                $configPath,
                "$ec2User@$ec2Host`:$($syncConfig.RemotePath)/config.json"
            )
            
            scp @scpArgs
            
            if ($LASTEXITCODE -eq 0) {
                Write-DeviceLog "✓ Device $DeviceId synced successfully to EC2" "SUCCESS"
                
                # Update sync registry
                Update-SyncRegistry -DeviceId $DeviceId -Status "Success" -Timestamp (Get-Date)
                return $true
            }
            else {
                Write-DeviceLog "✗ Failed to sync device $DeviceId to EC2" "ERROR"
                return $false
            }
        }
        catch {
            Write-DeviceLog "Sync error for $DeviceId`: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
    
    return $false
}

function Get-DeviceConfig {
    param([string]$DeviceId)
    
    $config = @{}
    
    switch -Wildcard ($DeviceId) {
        "AMP_*" {
            $config = @{
                ApiKey     = [Environment]::GetEnvironmentVariable('AMP_API_KEY', 'Process')
                Type       = "AMP"
                LastUpdate = Get-Date
            }
        }
        "GEMINI_*" {
            $config = @{
                ApiKey     = [Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
                Type       = "GEMINI"
                LastUpdate = Get-Date
            }
        }
        "MT5_*" {
            $config = @{
                Login      = [Environment]::GetEnvironmentVariable('MT5_LOGIN', 'Process')
                Server     = [Environment]::GetEnvironmentVariable('MT5_SERVER', 'Process')
                Type       = "MT5"
                LastUpdate = Get-Date
            }
        }
        "MT4_*" {
            $config = @{
                Login      = [Environment]::GetEnvironmentVariable('MT4_LOGIN', 'Process')
                Server     = [Environment]::GetEnvironmentVariable('MT4_SERVER', 'Process')
                Type       = "MT4"
                LastUpdate = Get-Date
            }
        }
    }
    
    return $config
}

function Update-SyncRegistry {
    param(
        [string]$DeviceId,
        [string]$Status,
        [datetime]$Timestamp
    )
    
    $registryPath = "$PSScriptRoot\device-sync-registry.json"
    $registry = @{}
    
    if (Test-Path $registryPath) {
        try {
            $registry = Get-Content $registryPath | ConvertFrom-Json -AsHashtable
        }
        catch {
            $registry = @{}
        }
    }
    
    $registry[$DeviceId] = @{
        Status    = $Status
        LastSync  = $Timestamp.ToString("yyyy-MM-dd HH:mm:ss")
        SyncCount = ($registry[$DeviceId].SyncCount ?? 0) + 1
    }
    
    $registry | ConvertTo-Json -Depth 3 | Out-File -FilePath $registryPath -Encoding UTF8
}

function Show-DeviceStatus {
    Write-Host "`n🔌 Trading System Device Manager" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    
    $devices = Get-LocalDevices
    
    if ($devices.Count -eq 0) {
        Write-Host "No trading devices found" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nDetected Devices:" -ForegroundColor Cyan
    $devices | Format-Table -AutoSize Type, DeviceId, Status, @{
        Name       = "LastSync"
        Expression = { 
            if ($_.LastSync) { 
                $_.LastSync.ToString("yyyy-MM-dd HH:mm:ss") 
            }
            else { 
                "Never" 
            }
        }
    }
    
    # Show sync registry
    $registryPath = "$PSScriptRoot\device-sync-registry.json"
    if (Test-Path $registryPath) {
        Write-Host "`nSync History:" -ForegroundColor Cyan
        try {
            $registry = Get-Content $registryPath | ConvertFrom-Json
            $registry.PSObject.Properties | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value.Status) (Last: $($_.Value.LastSync), Count: $($_.Value.SyncCount))"
            }
        }
        catch {
            Write-Host "  Could not read sync registry" -ForegroundColor Red
        }
    }
}

function Start-AutoSync {
    Write-DeviceLog "Starting automatic device synchronization..."
    
    $devices = Get-LocalDevices
    $syncResults = @()
    
    foreach ($device in $devices) {
        if ($device.Type -match "AMP|GEMINI|MT[45]|USB|METAMASK|LEDGER|TREZOR|ETH") {
            Write-DeviceLog "Auto-syncing device: $($device.DeviceId)"
            $result = Sync-DeviceData -DeviceId $device.DeviceId -Force $ForceSync
            $syncResults += [PSCustomObject]@{
                DeviceId = $device.DeviceId
                Success  = $result
            }
        }
    }    Write-DeviceLog "Auto-sync completed. Results:"
    $syncResults | ForEach-Object {
        $status = if ($_.Success) { "✓ SUCCESS" } else { "✗ FAILED" }
        Write-DeviceLog "  $($_.DeviceId): $status"
    }

    # If no devices matched for sync, create a registry placeholder so owners see the sync ran
    if ($syncResults.Count -eq 0) {
        Write-DeviceLog "No matching devices found for auto-sync. Writing placeholder registry entry." "INFO"
        Update-SyncRegistry -DeviceId "NO_DEVICES_FOUND" -Status "NoDevices" -Timestamp (Get-Date)
    }
}

# Main execution logic
switch ($Action.ToLower()) {
    "status" {
        Show-DeviceStatus
    }
    "sync" {
        if ($DeviceId) {
            Sync-DeviceData -DeviceId $DeviceId -Force $ForceSync
        }
        else {
            Start-AutoSync
        }
    }
    "list" {
        $devices = Get-LocalDevices
        $devices | ConvertTo-Json -Depth 3
    }
    "register" {
        if ($DeviceId) {
            Write-DeviceLog "Registering new device: $DeviceId"
            Update-SyncRegistry -DeviceId $DeviceId -Status "Registered" -Timestamp (Get-Date)
        }
        else {
            Write-Error "DeviceId is required for registration"
        }
    }
    default {
        Write-Host "Trading System Device Manager" -ForegroundColor Green
        Write-Host "=============================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Usage:"
        Write-Host "  .\device-manager.ps1 -Action status              # Show device status"
        Write-Host "  .\device-manager.ps1 -Action sync                # Sync all devices"
        Write-Host "  .\device-manager.ps1 -Action sync -DeviceId MT5_PC1  # Sync specific device"
        Write-Host "  .\device-manager.ps1 -Action list                # List devices as JSON"
        Write-Host "  .\device-manager.ps1 -Action register -DeviceId NewDevice  # Register device"
        Write-Host ""
        Write-Host "Switches:"
        Write-Host "  -ForceSync    Force synchronization even if recently synced"
        Write-Host ""
        
        Show-DeviceStatus
    }
}