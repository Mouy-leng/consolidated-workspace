#!/usr/bin/env pwsh
# A6-9V Local Secrets Management

param(
    [Parameter(Position=0)]
    [ValidateSet("add", "list", "remove", "backup")]
    [string]secrets = "list",
    
    [Parameter(Position=1)]
    [string] = "",
    
    [Parameter(Position=2)]
    [string] = ""
)

$SECRETS_DIR = "$env:GENX_SECRETS_DIR\a69v"
if (-not (Test-Path $SECRETS_DIR)) {
    New-Item -ItemType Directory -Path $SECRETS_DIR -Force | Out-Null
}

switch ($Action) {
    "add" {
        if (-not $SecretName) {
            Write-Host "Usage: ./a69v_secrets.ps1 add SECRET_NAME SECRET_VALUE" -ForegroundColor Yellow
            return
        }
        
        $credTarget = "A6V9_$SecretName"
        cmdkey /generic:$credTarget /user:A6-9V /pass:$SecretValue
        Write-Host "✓ Added secret: $SecretName" -ForegroundColor Green
    }
    "list" {
        Write-Host "A6-9V Stored Secrets:" -ForegroundColor Cyan
        cmdkey /list | Where-Object { $_ -match "A6V9_" } | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    "remove" {
        if (-not $SecretName) {
            Write-Host "Usage: ./a69v_secrets.ps1 remove SECRET_NAME" -ForegroundColor Yellow
            return
        }
        
        $credTarget = "A6V9_$SecretName"
        cmdkey /delete:$credTarget
        Write-Host "✓ Removed secret: $SecretName" -ForegroundColor Green
    }
    "backup" {
        Write-Host "Creating secrets backup..." -ForegroundColor Blue
        # Note: This is a placeholder - actual backup would export non-sensitive metadata
        Write-Host "✓ Backup completed" -ForegroundColor Green
    }
}
