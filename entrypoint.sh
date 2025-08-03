#!/bin/bash

echo "🧠 Installing Playwright browsers..."
playwright install --with-deps

echo "🚀 Starting Streamlit app..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
