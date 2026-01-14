# Todo API Backend

Phase 2 Todo Web Application Backend - FastAPI + SQLModel + Neon PostgreSQL

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn src.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `SECRET_KEY`: JWT secret key for session tokens
- `FRONTEND_URL`: Frontend origin for CORS

## API Endpoints

### Health
- `GET /` - Root health check
- `GET /health` - Health check endpoint

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/signin` - Sign in user
- `POST /api/v1/auth/signout` - Sign out user
- `GET /api/v1/auth/session` - Get current session

### Todos
- `GET /api/v1/todos` - List todos (paginated)
- `POST /api/v1/todos` - Create todo
- `GET /api/v1/todos/{id}` - Get todo by ID
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo

## Deployment

### Docker

```bash
# Build image
docker build -t todo-api .

# Run container
docker run -p 8000:8000 --env-file .env todo-api
```

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will auto-deploy on push to main

Required secrets:
- `DATABASE_URL`
- `SECRET_KEY`
- `FRONTEND_URL`

## Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src
```

## GitHub Secrets Configuration

For CI/CD deployment, configure these secrets in your GitHub repository:

### Backend (Railway)
- `RAILWAY_TOKEN` - Railway API token for deployment

### Frontend (Vercel)
- `VERCEL_TOKEN` - Vercel API token for deployment

### How to get tokens:
1. **Railway**: Go to Railway dashboard → Account Settings → Tokens → Create Token
2. **Vercel**: Go to Vercel dashboard → Settings → Tokens → Create Token

### Environment Variables (set in deployment platform):
- `DATABASE_URL` - Neon PostgreSQL connection string
- `SECRET_KEY` - JWT secret for session tokens (generate with `openssl rand -hex 32`)
- `FRONTEND_URL` - Frontend URL for CORS (e.g., `https://your-app.vercel.app`)
