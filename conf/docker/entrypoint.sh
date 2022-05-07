#!/bin/sh

python /app/src/utils/wait_for_elastic.py
python -m gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Run the main container process
exec "$@"
