FROM python:3.11-slim

WORKDIR /app

# Copy backend
COPY backend/ ./backend/

# Install dependencies
RUN pip install -r backend/requirements.txt

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "backend/app.py"]