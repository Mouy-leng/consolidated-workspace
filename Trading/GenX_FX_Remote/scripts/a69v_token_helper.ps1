#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V Token Usage Helper
.DESCRIPTION
    Helper script to use stored A6-9V GitHub token for various operations.
#>

# Get A6-9V GitHub Token
function Get-A69VToken {
    if ($env:A69V_GITHUB_TOKEN) {
        return $env:A69V_GITHUB_TOKEN
    } elseif ($env:GH_TOKEN) {
        return $env:GH_TOKEN
    } else {
        Write-Warning "A6-9V GitHub token not found in environment variables"
        return $null
    }
}

# Set token for GitHub CLI
function Set-GHToken {
    $token = Get-A69VToken
    if ($token) {
        $env:GH_TOKEN = $token
        Write-Host "✓ GitHub CLI token configured for A6-9V" -ForegroundColor Green
        return $true
    }
    return $false
}

# Verify token access
function Test-A69VTokenAccess {
    $token = Get-A69VToken
    if (-not $token) {
        Write-Host "✗ No A6-9V GitHub token found" -ForegroundColor Red
        return $false
    }
    
    try {
        # Test token with GitHub API
        $headers = @{
            "Authorization" = "Bearer $token"
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "A6-9V-PowerShell"
        }
        
        $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method Get
        Write-Host "✓ Token valid for user: $($response.login)" -ForegroundColor Green
        Write-Host "  Name: $($response.name)" -ForegroundColor Gray
        Write-Host "  Public repos: $($response.public_repos)" -ForegroundColor Gray
        return $true
        
    } catch {
        Write-Host "✗ Token validation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Auto-configure if running directly
Write-Host "🎯 A6-9V Token Usage Helper" -ForegroundColor Magenta

if (Set-GHToken) {
    Test-A69VTokenAccess
}

# Export functions for module use (only when imported as module)
if ($MyInvocation.InvocationName -eq '&') {
    Export-ModuleMember -Function Get-A69VToken, Set-GHToken, Test-A69VTokenAccess
}
