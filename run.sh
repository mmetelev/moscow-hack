#!/bin/bash

#exec uvicorn fastapi_.fastapp:app --reload &
exec streamlit run 00_MAIN.py --server.port 8501 &