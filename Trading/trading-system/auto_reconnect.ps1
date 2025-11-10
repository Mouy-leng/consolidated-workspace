# Auto-reconnect after TECNO disconnect
$backupNetworks = Find-BackupConnections
if ($backupNetworks.Count -gt 0) {
    $bestBackup = $backupNetworks | Sort-Object { [int]$_.Signal } -Descending | Select-Object -First 1
    Write-Host "🔄 Attempting backup connection: $($bestBackup.SSID)" -ForegroundColor Cyan
    netsh wlan connect name="$($bestBackup.SSID)"
}
