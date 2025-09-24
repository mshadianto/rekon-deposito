#!/bin/bash
echo "� Setting up Multi-Bank Reconciliation System..."
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: ./scripts/run.sh"
