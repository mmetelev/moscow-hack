#!/bin/bash

#exec uvicorn fastapi_.fastapp:app --reload &
exec streamlit run st_app.py --server.port 8501 &