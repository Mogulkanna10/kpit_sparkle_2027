#!/usr/bin/env bash
echo "Setting up AURA-Impact Environment..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install tree-sitter tree-sitter-c faiss-cpu streamlit
echo "[OK] Setup completed successfully."
