#!/bin/sh

# running migrations
poetry run alembic upgrade head

# running the application
poetry run uvicorn --host 0.0.0.0 --port 8000 site_ong.main:app