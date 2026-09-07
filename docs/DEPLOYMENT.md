# Deployment Guide

The Urban Flood Nowcasting System is production-oriented and deployable locally, in containers via Docker Compose, or on cloud platforms (AWS, GCP, Azure, Render, Railway).

---

## Option 1: Native Local Development (Zero-Config)

### Prerequisites:
- Python 3.10+
- Node.js 18+ and npm

### 1. Start the Backend:
```bash
# In the project root
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`
- Uses SQLite database automatically (`flood_nowcasting.db`).

### 2. Start the Frontend:
```bash
cd frontend
npm run dev
```
- Open browser at `http://localhost:3000`

---

## Option 2: Docker Compose Deployment (Production-Ready)

The system includes a complete containerized stack:
- **PostgreSQL 16 + PostGIS 3.4** (Spatial Database)
- **Redis 7** (In-memory Cache & Task Queue)
- **FastAPI Backend Container**
- **Next.js Frontend Container**

### Commands:
```bash
# Build and launch all services
docker compose up --build -d

# Check service logs
docker compose logs -f

# Verify service health
docker compose ps
```
- Web Application: `http://localhost:3000`
- REST API & Swagger UI: `http://localhost:8000/docs`

---

## Option 3: Cloud Deployment

### Backend (e.g. Render, Railway, AWS ECS / Cloud Run):
1. Build container using `infrastructure/Dockerfile.backend`.
2. Provide environment variables:
   - `DATABASE_URL`: Managed PostgreSQL with PostGIS extension.
   - `OPEN_METEO_FORECAST_URL`: `https://api.open-meteo.com/v1/forecast`
   - `OPEN_METEO_ELEVATION_URL`: `https://api.open-meteo.com/v1/elevation`
   - `SECRET_KEY`: Strong cryptographic key.
3. Expose port `8000`.

### Frontend (e.g. Vercel, Netlify, Cloud Run):
1. Deploy `frontend/` directory.
2. Set environment variable:
   - `NEXT_PUBLIC_API_URL`: Backend public API URL (e.g. `https://api.flood-nowcast.lpu.in/api/v1`).
