# Starts FastAPI backend and Vite frontend concurrently in separate windows.
# Usage: npm run dev:all

$ErrorActionPreference = 'Stop'

Write-Host 'Starting FastAPI backend (port 8000)...'
Start-Process powershell -ArgumentList '-NoExit','-Command','uvicorn app.main:app --reload --port 8000' -WindowStyle Minimized

Write-Host 'Ensuring frontend dependencies installed...'
npm install --prefix frontend | Out-Null

Write-Host 'Starting Vite frontend (port 5173)...'
npm run dev --prefix frontend
