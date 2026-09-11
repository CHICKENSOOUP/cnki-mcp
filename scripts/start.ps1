[CmdletBinding()]
param(
    [switch]$Stop,
    [switch]$Logs,
    [ValidateRange(10, 600)]
    [int]$WaitSeconds = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker was not found. Install and start Docker Desktop, then run this script again."
}

if ($Stop) {
    docker compose down
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath (Join-Path $root "docker-compose.yml"))) {
    throw "docker-compose.yml was not found. Run this script from the project checkout."
}

docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is installed but not running. Start Docker Desktop, then try again."
}

Write-Host "Building and starting CNKI Scholar..."
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose could not start the service."
}

$deadline = (Get-Date).AddSeconds($WaitSeconds)
$healthy = $false
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $healthy) {
    Write-Host "The service did not become healthy within $WaitSeconds seconds." -ForegroundColor Red
    docker compose ps
    docker compose logs --tail=100
    exit 1
}

Write-Host "CNKI Scholar is ready: http://127.0.0.1:8000/mcp" -ForegroundColor Green
Write-Host "Health check: http://127.0.0.1:8000/health"

if ($Logs) {
    docker compose logs -f cnki-mcp
}
