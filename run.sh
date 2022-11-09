#!/bin/bash

# Run both interfaces in parallel
#exec uvicorn fastapi_app.fastapp:app --port 8080 --host 0.0.0.0 --reload &
exec streamlit run --server.port 8503 --server.enableCORS false 00_MAIN.py &