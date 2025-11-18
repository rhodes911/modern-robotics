# Create venv and install dependencies
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Environment ready. Activate with: . .\\.venv\\Scripts\\Activate.ps1"