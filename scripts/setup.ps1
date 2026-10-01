# PowerShell Setup Script for AURA-Impact
Write-Host "Setting up AURA-Impact Environment..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install tree-sitter tree-sitter-c faiss-cpu streamlit
Write-Host "[OK] Setup completed successfully."
