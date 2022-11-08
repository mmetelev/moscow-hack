#!/bin/bash

# Run both interfaces in parallel
exec uvicorn fastapi_app.fastapp:app --port 8000 --host 0.0.0.0 --reload &
exec streamlit run 00_MAIN.py --server.port 8501 &