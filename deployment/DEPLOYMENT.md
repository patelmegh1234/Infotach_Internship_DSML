<!-- Megh, Upload Date: 2026-07-28 -->
# Deployment Notes

## Local Docker

```bash
docker compose up --build
```

## Production Direction

For the final project, deploy frontend and backend separately:

- Backend container runs FastAPI and the trained model artifact.
- Frontend is built as static assets and served through a CDN or Nginx.
- Upload limit, CORS origins, and model mode are environment variables.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | Runtime environment |
| `CORS_ORIGINS` | Allowed frontend origins |
| `MAX_UPLOAD_MB` | Upload size limit |
| `MODEL_MODE` | `baseline` now, `ast` later |
| `VITE_API_BASE_URL` | Frontend API target |

