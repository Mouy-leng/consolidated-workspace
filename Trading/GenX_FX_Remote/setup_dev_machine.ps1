# Development Machine Setup Script
# Run this script as Administrator

Write-Host "=== Development Machine Setup Script ===" -ForegroundColor Green
Write-Host "This script will configure your machine for development work" -ForegroundColor Yellow

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Red
    exit 1
}

Write-Host "Running with Administrator privileges..." -ForegroundColor Green

# Function to safely set permissions
function Set-DrivePermissions {
    param($DriveLetter)
    
    Write-Host "Setting permissions for drive $DriveLetter..." -ForegroundColor Cyan
    
    try {
        # Grant full control to Users group
        icacls "${DriveLetter}:\" /grant "Users:(OI)(CI)F" /T
        Write-Host "Successfully set permissions for $DriveLetter drive" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Could not set permissions for $DriveLetter drive: $_" -ForegroundColor Yellow
    }
}

# Function to initialize and format a new drive
function Initialize-NewDrive {
    param($DiskNumber)
    
    Write-Host "Initializing disk $DiskNumber..." -ForegroundColor Cyan
    
    try {
        # Initialize the disk with GPT partition style
        Initialize-Disk -Number $DiskNumber -PartitionStyle GPT -Confirm:$false
        
        # Create a new partition using all available space
        $partition = New-Partition -DiskNumber $DiskNumber -UseMaximumSize -AssignDriveLetter
        
        # Format the partition as NTFS
        Format-Volume -DriveLetter $partition.DriveLetter -FileSystem NTFS -NewFileSystemLabel "DEVELOPMENT" -Confirm:$false
        
        Write-Host "Successfully initialized disk $DiskNumber as drive $($partition.DriveLetter)" -ForegroundColor Green
        
        # Set permissions for the new drive
        Set-DrivePermissions -DriveLetter $partition.DriveLetter
        
        return $partition.DriveLetter
    }
    catch {
        Write-Host "Error initializing disk $DiskNumber`: $_" -ForegroundColor Red
        return $null
    }
}

# Check for uninitialized disks
Write-Host "Checking for uninitialized disks..." -ForegroundColor Cyan
$uninitializedDisks = Get-Disk | Where-Object {$_.PartitionStyle -eq 'RAW'}

if ($uninitializedDisks) {
    Write-Host "Found uninitialized disk(s):" -ForegroundColor Yellow
    $uninitializedDisks | Format-Table Number, FriendlyName, Size, HealthStatus -AutoSize
    
    foreach ($disk in $uninitializedDisks) {
        $response = Read-Host "Do you want to initialize and format disk $($disk.Number) - $($disk.FriendlyName)? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            $newDriveLetter = Initialize-NewDrive -DiskNumber $disk.Number
            if ($newDriveLetter) {
                Write-Host "New drive $newDriveLetter`: is ready for use!" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "No uninitialized disks found." -ForegroundColor Green
}

# Set permissions for existing drives
Write-Host "Configuring permissions for existing drives..." -ForegroundColor Cyan

$drives = Get-Volume | Where-Object {$_.DriveType -eq 'Fixed' -and $_.DriveLetter}
foreach ($drive in $drives) {
    if ($drive.DriveLetter -ne 'C') {  # Skip system drive for safety
        Set-DrivePermissions -DriveLetter $drive.DriveLetter
    } else {
        Write-Host "Skipping system drive C: for safety" -ForegroundColor Yellow
        Write-Host "You can manually set specific folder permissions if needed" -ForegroundColor Yellow
    }
}

# Create development directories with proper permissions
Write-Host "Creating development directories..." -ForegroundColor Cyan

$devPaths = @(
    "C:\Dev",
    "C:\Dev\Projects",
    "C:\Dev\Tools",
    "C:\Dev\Workspace"
)

foreach ($path in $devPaths) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force
        Write-Host "Created directory: $path" -ForegroundColor Green
        
        # Set full permissions for all users on development directories
        icacls $path /grant "Users:(OI)(CI)F" /T
    }
}

# Enable Developer Mode (if Windows 10/11)
Write-Host "Enabling Windows Developer Mode..." -ForegroundColor Cyan
try {
    $registryKeyPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    
    if (-not (Test-Path $registryKeyPath)) {
        New-Item -Path $registryKeyPath -ItemType Directory -Force
    }
    
    New-ItemProperty -Path $registryKeyPath -Name AllowDevelopmentWithoutDevLicense -PropertyType DWORD -Value 1 -Force
    New-ItemProperty -Path $registryKeyPath -Name AllowAllTrustedApps -PropertyType DWORD -Value 1 -Force
    
    Write-Host "Developer mode enabled successfully" -ForegroundColor Green
}
catch {
    Write-Host "Warning: Could not enable developer mode: $_" -ForegroundColor Yellow
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Your development machine is now configured!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Install development tools (Cursor, VS Code, etc.)" -ForegroundColor White
Write-Host "2. Connect and initialize your 2.5 SATA drive if not already done" -ForegroundColor White
Write-Host "3. Configure your development environment" -ForegroundColor White

Read-Host "Press Enter to exit"