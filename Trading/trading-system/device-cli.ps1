# Trading System Device CLI
# Command-line interface for managing devices and plugins

param(
    [string]$Command = "help",
    [string]$DeviceId = "",
    [string]$Type = "",
    [hashtable]$Config = @{},
    [switch]$Force = $false,
    [switch]$Auto = $false
)

# Load environment configuration
. "$PSScriptRoot\load-env.ps1"

$microserviceUrl = "http://localhost:3000"

function Invoke-DeviceApi {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    $uri = "$microserviceUrl/api/v1/$Endpoint"
    
    try {
        $params = @{
            Uri         = $uri
            Method      = $Method
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 3)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Error "API call failed: $($_.Exception.Message)"
        return $null
    }
}

function Show-DeviceList {
    Write-Host "📱 Trading System Devices" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    
    $response = Invoke-DeviceApi -Endpoint "devices"
    
    if ($response -and $response.success) {
        if ($response.devices.Count -eq 0) {
            Write-Host "No devices registered" -ForegroundColor Yellow
            return
        }
        
        Write-Host ""
        $response.devices | Format-Table -Property @(
            @{Name = "Device ID"; Expression = { $_.deviceId }; Width = 12 },
            @{Name = "Type"; Expression = { $_.type }; Width = 15 },
            @{Name = "Name"; Expression = { $_.name }; Width = 20 },
            @{Name = "Status"; Expression = { $_.status }; Width = 10 },
            @{Name = "Last Sync"; Expression = {
                    if ($_.lastSync) { 
                        [DateTime]::Parse($_.lastSync).ToString("MM/dd HH:mm") 
                    }
                    else { 
                        "Never" 
                    }
                }; Width = 12
            }
        )
        
        Write-Host "Total devices: $($response.total)" -ForegroundColor Cyan
    }
    else {
        Write-Host "❌ Failed to retrieve devices" -ForegroundColor Red
    }
}

function Show-SyncStatus {
    Write-Host "🔄 Device Sync Status" -ForegroundColor Green
    Write-Host "====================" -ForegroundColor Green
    
    $response = Invoke-DeviceApi -Endpoint "devices/sync-status"
    
    if ($response -and $response.success) {
        Write-Host ""
        Write-Host "📊 Summary:" -ForegroundColor Cyan
        Write-Host "  Total Devices: $($response.totalDevices)"
        Write-Host "  Online: $($response.onlineDevices)" -ForegroundColor Green
        Write-Host "  Syncing: $($response.syncingDevices)" -ForegroundColor Yellow
        Write-Host "  Errors: $($response.errorDevices)" -ForegroundColor Red
        Write-Host "  Service Running: $($response.isRunning)"
        Write-Host ""
        
        if ($response.devices.Count -gt 0) {
            Write-Host "🔍 Device Details:" -ForegroundColor Cyan
            $response.devices | ForEach-Object {
                $statusColor = switch ($_.status) {
                    "online" { "Green" }
                    "syncing" { "Yellow" }
                    "error" { "Red" }
                    default { "Gray" }
                }
                
                Write-Host "  [$($_.deviceId)] $($_.name) - " -NoNewline
                Write-Host $_.status -ForegroundColor $statusColor
            }
        }
    }
    else {
        Write-Host "❌ Failed to retrieve sync status" -ForegroundColor Red
    }
}

function Register-Device {
    param(
        [string]$DeviceType,
        [string]$DeviceName,
        [hashtable]$DeviceConfig
    )
    
    if (-not $DeviceType) {
        Write-Error "Device type is required"
        return
    }
    
    if (-not $DeviceName) {
        $DeviceName = "Device-$(Get-Random -Minimum 1000 -Maximum 9999)"
    }
    
    Write-Host "📱 Registering new device..." -ForegroundColor Yellow
    Write-Host "  Type: $DeviceType"
    Write-Host "  Name: $DeviceName"
    
    $deviceInfo = @{
        type         = $DeviceType
        name         = $DeviceName
        config       = $DeviceConfig
        capabilities = @()
        metadata     = @{
            registeredBy = "CLI"
            registeredAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
    }
    
    # Add default capabilities based on type
    switch ($DeviceType) {
        "mt5-terminal" {
            $deviceInfo.capabilities = @("trading", "market-data", "expert-advisors")
        }
        "mt4-terminal" {
            $deviceInfo.capabilities = @("trading", "market-data", "expert-advisors")
        }
        "amp-api" {
            $deviceInfo.capabilities = @("trading", "market-data", "order-management")
        }
        "gemini-api" {
            $deviceInfo.capabilities = @("trading", "market-data", "order-management")
        }
        default {
            $deviceInfo.capabilities = @("generic")
        }
    }
    
    $response = Invoke-DeviceApi -Endpoint "devices/register" -Method "POST" -Body $deviceInfo
    
    if ($response -and $response.success) {
        Write-Host "✅ Device registered successfully" -ForegroundColor Green
        Write-Host "  Device ID: $($response.device.deviceId)" -ForegroundColor Cyan
        Write-Host "  Status: $($response.device.status)"
        return $response.device
    }
    else {
        Write-Host "❌ Failed to register device" -ForegroundColor Red
        return $null
    }
}

function Sync-Device {
    param(
        [string]$DeviceId,
        [bool]$Force = $false
    )
    
    if (-not $DeviceId) {
        Write-Error "Device ID is required"
        return
    }
    
    Write-Host "🔄 Syncing device: $DeviceId" -ForegroundColor Yellow
    
    $syncData = @{
        force = $Force
    }
    
    $response = Invoke-DeviceApi -Endpoint "devices/$DeviceId/sync" -Method "POST" -Body $syncData
    
    if ($response -and $response.success) {
        Write-Host "✅ Device sync completed" -ForegroundColor Green
        Write-Host "  Message: $($response.message)"
        
        if ($response.device) {
            Write-Host "  Status: $($response.device.status)"
        }
    }
    else {
        Write-Host "❌ Device sync failed" -ForegroundColor Red
        if ($response.error) {
            Write-Host "  Error: $($response.error)" -ForegroundColor Red
        }
    }
}

function Sync-AllDevices {
    param([bool]$Force = $false)
    
    Write-Host "🔄 Syncing all devices..." -ForegroundColor Yellow
    
    $syncData = @{
        force = $Force
    }
    
    $response = Invoke-DeviceApi -Endpoint "devices/sync-all" -Method "POST" -Body $syncData
    
    if ($response -and $response.success) {
        Write-Host "✅ Bulk sync completed" -ForegroundColor Green
        Write-Host "  $($response.message)"
        Write-Host "  Successful: $($response.summary.successful)/$($response.summary.total)"
        
        if ($response.summary.failed -gt 0) {
            Write-Host "  Failed devices:" -ForegroundColor Red
            $response.results | Where-Object { -not $_.success } | ForEach-Object {
                Write-Host "    - $($_.deviceId): $($_.error)" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "❌ Bulk sync failed" -ForegroundColor Red
    }
}

function Remove-Device {
    param([string]$DeviceId)
    
    if (-not $DeviceId) {
        Write-Error "Device ID is required"
        return
    }
    
    Write-Host "🗑️ Removing device: $DeviceId" -ForegroundColor Yellow
    
    if (-not $Force) {
        $confirm = Read-Host "Are you sure you want to remove this device? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Operation cancelled" -ForegroundColor Red
            return
        }
    }
    
    $response = Invoke-DeviceApi -Endpoint "devices/$DeviceId" -Method "DELETE"
    
    if ($response -and $response.success) {
        Write-Host "✅ Device removed successfully" -ForegroundColor Green
        Write-Host "  $($response.message)"
    }
    else {
        Write-Host "❌ Failed to remove device" -ForegroundColor Red
    }
}

function Test-MicroserviceConnection {
    Write-Host "🧪 Testing microservice connection..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$microserviceUrl/health" -Method GET
        
        if ($response.status -eq "healthy") {
            Write-Host "✅ Microservice is healthy" -ForegroundColor Green
            Write-Host "  Service: $($response.service)"
            Write-Host "  Version: $($response.version)"
            Write-Host "  Uptime: $([math]::Round($response.uptime, 2)) seconds"
            return $true
        }
    }
    catch {
        Write-Host "❌ Microservice connection failed" -ForegroundColor Red
        Write-Host "  URL: $microserviceUrl"
        Write-Host "  Error: $($_.Exception.Message)"
        Write-Host ""
        Write-Host "💡 Make sure the trading microservice is running:" -ForegroundColor Yellow
        Write-Host "  cd trading-microservice"
        Write-Host "  npm start"
        Write-Host "  # or"
        Write-Host "  docker-compose up -d"
        return $false
    }
}

function Auto-DiscoverDevices {
    Write-Host "🔍 Auto-discovering devices..." -ForegroundColor Yellow
    
    $discoveredDevices = @()
    
    # Check for MT5
    $mt5Process = Get-Process -Name "metatrader5" -ErrorAction SilentlyContinue
    if ($mt5Process) {
        Write-Host "📊 Found MetaTrader 5 terminal" -ForegroundColor Cyan
        $mt5Device = Register-Device -DeviceType "mt5-terminal" -DeviceName "MT5 Terminal" -DeviceConfig @{
            processId = $mt5Process.Id
            path      = $mt5Process.Path
        }
        if ($mt5Device) {
            $discoveredDevices += $mt5Device
        }
    }
    
    # Check for MT4
    $mt4Process = Get-Process -Name "metatrader4" -ErrorAction SilentlyContinue
    if ($mt4Process) {
        Write-Host "📊 Found MetaTrader 4 terminal" -ForegroundColor Cyan
        $mt4Device = Register-Device -DeviceType "mt4-terminal" -DeviceName "MT4 Terminal" -DeviceConfig @{
            processId = $mt4Process.Id
            path      = $mt4Process.Path
        }
        if ($mt4Device) {
            $discoveredDevices += $mt4Device
        }
    }
    
    # Check for API keys in environment
    $ampApiKey = [Environment]::GetEnvironmentVariable('AMP_API_KEY', 'Process')
    if ($ampApiKey) {
        Write-Host "🔑 Found AMP API key" -ForegroundColor Cyan
        $ampDevice = Register-Device -DeviceType "amp-api" -DeviceName "AMP Trading API" -DeviceConfig @{
            hasApiKey = $true
        }
        if ($ampDevice) {
            $discoveredDevices += $ampDevice
        }
    }
    
    $geminiApiKey = [Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
    if ($geminiApiKey) {
        Write-Host "🔑 Found Gemini API key" -ForegroundColor Cyan
        $geminiDevice = Register-Device -DeviceType "gemini-api" -DeviceName "Gemini API" -DeviceConfig @{
            hasApiKey = $true
        }
        if ($geminiDevice) {
            $discoveredDevices += $geminiDevice
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Auto-discovery completed" -ForegroundColor Green
    Write-Host "  Discovered $($discoveredDevices.Count) devices"
}

function Show-Help {
    Write-Host "📱 Trading System Device CLI" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  list                    - List all registered devices"
    Write-Host "  status                  - Show sync status"
    Write-Host "  register                - Register a new device"
    Write-Host "  sync                    - Sync specific device"
    Write-Host "  sync-all                - Sync all devices"
    Write-Host "  remove                  - Remove a device"
    Write-Host "  discover                - Auto-discover devices"
    Write-Host "  test                    - Test microservice connection"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -DeviceId <id>          - Target device ID"
    Write-Host "  -Type <type>            - Device type (mt5-terminal, amp-api, etc.)"
    Write-Host "  -Force                  - Force operation without confirmation"
    Write-Host "  -Auto                   - Auto-discover and register devices"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\device-cli.ps1 -Command list"
    Write-Host "  .\device-cli.ps1 -Command register -Type mt5-terminal"
    Write-Host "  .\device-cli.ps1 -Command sync -DeviceId abc123"
    Write-Host "  .\device-cli.ps1 -Command sync-all -Force"
    Write-Host "  .\device-cli.ps1 -Command discover"
    Write-Host ""
}

# Main execution
if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Test microservice connection first
if (-not (Test-MicroserviceConnection)) {
    exit 1
}

# Execute command
switch ($Command.ToLower()) {
    "list" {
        Show-DeviceList
    }
    "status" {
        Show-SyncStatus
    }
    "register" {
        if ($Auto) {
            Auto-DiscoverDevices
        }
        else {
            Register-Device -DeviceType $Type -DeviceName "" -DeviceConfig $Config
        }
    }
    "sync" {
        if ($DeviceId) {
            Sync-Device -DeviceId $DeviceId -Force $Force
        }
        else {
            Write-Error "DeviceId is required for sync command"
        }
    }
    "sync-all" {
        Sync-AllDevices -Force $Force
    }
    "remove" {
        if ($DeviceId) {
            Remove-Device -DeviceId $DeviceId
        }
        else {
            Write-Error "DeviceId is required for remove command"
        }
    }
    "discover" {
        Auto-DiscoverDevices
    }
    "test" {
        Test-MicroserviceConnection
    }
    default {
        Show-Help
    }
}