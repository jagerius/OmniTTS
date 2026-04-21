# Start_OmniTTS.ps1
# SkyrimNet OmniTTS Server Launcher
# Based on Start_CHATTERBOX.ps1

$ErrorActionPreference = "Continue"

# Banner
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  OmniTTS Server for SkyrimNet" -ForegroundColor Cyan
Write-Host "  Powered by OmniVoice (k2-fsa)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory to script location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check for venv
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
$venvActivate = Join-Path $scriptDir "venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_venv.bat first to create the virtual environment." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
& $venvActivate

# Set PYTHONPATH to include OmniVoice
$omniVoicePath = Join-Path (Split-Path $scriptDir -Parent) "OmniVoice"
if (Test-Path $omniVoicePath) {
    $env:PYTHONPATH = "$omniVoicePath;$env:PYTHONPATH"
    Write-Host "[INFO] OmniVoice path: $omniVoicePath" -ForegroundColor Green
} else {
    Write-Host "[WARN] OmniVoice directory not found at: $omniVoicePath" -ForegroundColor Yellow
}

# Set default port
$port = "7860"

# Check if --port was passed in the arguments to update the display variable
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--port" -and ($i + 1) -lt $args.Count) {
        $port = $args[$i + 1]
        break
    }
}

# Base arguments
$serverArgs = @("omnitts_server.py", "--server", "0.0.0.0")

# If the user didn't specify a port, add the default one
if ($args -notcontains "--port") {
    $serverArgs += "--port", $port
}

# Add any extra arguments passed to this script
if ($args.Count -gt 0) {
    $serverArgs += $args
}

Write-Host ""
Write-Host "[INFO] Starting OmniTTS server..." -ForegroundColor Green
Write-Host "[INFO] Endpoint: http://localhost:$port" -ForegroundColor Green
Write-Host "[INFO] API: http://localhost:$port/api/generate_audio" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start with high priority
$process = Start-Process -FilePath $venvPython -ArgumentList $serverArgs -NoNewWindow -PassThru
if ($process) {
    try {
        $process.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
        Write-Host "[INFO] Process priority set to HIGH" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Could not set process priority" -ForegroundColor Yellow
    }
    $process.WaitForExit()
} else {
    # Fallback: run directly
    & $venvPython $serverArgs
}
