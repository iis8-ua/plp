FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# El contexto de build es la raíz del repo: necesitamos backend/ y api/.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY api/ ./api/

# settings.py ya añade la raíz al sys.path; esto lo hace explícito para gunicorn.
ENV PYTHONPATH=/app/backend:/app \
    DJANGO_SETTINGS_MODULE=tpv.settings

WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "tpv.wsgi:application", "--bind", "0.0.0.0:8000"]
