if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: Node.js is not installed. Download it from https://nodejs.org/"
    exit 1
}

# Check for Python + pip
$python = @("python", "python3") | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
if (-not $python) {
    Write-Error "ERROR: Python is not installed. Download it from https://www.python.org/downloads/"
    exit 1
}

# Verify pip is installed
try {
    $pipVersion = & $python -m pip --version
    Write-Host "pip is installed ($pipVersion)"
} catch {
    Write-Error "ERROR: pip is missing. Install it with: $python -m ensurepip --upgrade"
    exit 1
}
# Verify versions (optional)


$nodeVersion = node --version
$pythonVersion = (& $python --version 2>&1) -join " "
Write-Host "Using Node.js $nodeVersion and Python $pythonVersion"

# Install Python dependencies
& $python -m pip install -r requirements.txt