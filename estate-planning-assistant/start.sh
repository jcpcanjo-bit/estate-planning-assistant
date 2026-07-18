#!/bin/zsh
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Checking dependencies..."
.venv/bin/pip install -q -r requirements.txt

# Skip Streamlit email prompt
mkdir -p "$HOME/.streamlit"
if [ ! -f "$HOME/.streamlit/credentials.toml" ]; then
  printf '[general]\nemail = ""\n' > "$HOME/.streamlit/credentials.toml"
fi

echo ""
echo "========================================"
echo "  Estate Planning Assistant"
echo "  Open:  http://localhost:8501"
echo "  Stop:  Ctrl+C"
echo "========================================"
echo ""

exec .venv/bin/streamlit run app.py --browser.gatherUsageStats false
