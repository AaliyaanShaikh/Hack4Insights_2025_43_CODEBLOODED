#!/bin/bash
# BearCart Dashboard Launcher Script

echo "🐻 BearCart Analytics Dashboard"
echo "================================"
echo ""

# Check if data cleaning is needed
if [ ! -d "data/cleaned" ] || [ -z "$(ls -A data/cleaned 2>/dev/null)" ]; then
    echo "⚠️  Cleaned data not found. Running data cleaning..."
    python3 -m backend.data_cleaning
    echo ""
fi

echo "🚀 Starting Streamlit dashboard..."
echo "Dashboard will open at http://localhost:8501"
echo ""
streamlit run frontend/app.py

