# Noir Luxe Economy Backend PowerShell Scripts

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  dev         - Start development server" -ForegroundColor Yellow
    Write-Host "  install     - Install dependencies" -ForegroundColor Yellow
    Write-Host "  seed-demo   - Seed demo data" -ForegroundColor Yellow
    Write-Host "  reset-demo  - Reset demo database" -ForegroundColor Yellow
    Write-Host "  test        - Run tests" -ForegroundColor Yellow
    Write-Host "  clean       - Clean cache files" -ForegroundColor Yellow
}

function Start-Dev {
    Write-Host "Starting development server..." -ForegroundColor Green
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Seed-Demo {
    Write-Host "Seeding demo data..." -ForegroundColor Green
    curl -X POST http://127.0.0.1:8000/api/demo/seed
}

function Reset-Demo {
    Write-Host "Resetting demo database..." -ForegroundColor Green
    curl -X POST http://127.0.0.1:8000/api/demo/reset
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Green
    python -m pytest
}

function Clean-Cache {
    Write-Host "Cleaning cache files..." -ForegroundColor Green
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Name "*.egg-info" | Remove-Item -Recurse -Force
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "dev" { Start-Dev }
    "install" { Install-Dependencies }
    "seed-demo" { Seed-Demo }
    "reset-demo" { Reset-Demo }
    "test" { Run-Tests }
    "clean" { Clean-Cache }
    "help" { Show-Help }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help 
    }
}
