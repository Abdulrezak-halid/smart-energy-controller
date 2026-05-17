#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

if ! python -c "import streamlit, skfuzzy" 2>/dev/null; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

exec python -m streamlit run app.py --server.port "${PORT:-8501}"
