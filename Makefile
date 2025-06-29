run-backend:
	poetry run uvicorn backend.main:app --reload

run-frontend:
	streamlit run frontend/webapp.py