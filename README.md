# AI Floor Plan and Market Insights

🏡 **Intelligent real estate assistant that parses floor plans, enriches property data with market insights, and generates MLS-ready listings.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Development Workflow](#-development-workflow)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Phase 0 (Current - Foundation)
- ✅ Docker-based development environment
- ✅ Flask REST API with JWT authentication
- ✅ React frontend with mobile-first design
- ✅ Supabase database with Row Level Security
- ✅ Celery async task processing

### Phase 1 (In Progress - Data Ingestion)
- 🔨 Floor plan image upload
- 🔨 AI-powered floor plan parsing (Gemini Vision)
- 🔨 Address-based property search
- 🔨 User authentication system

### Phase 2 (Planned - AI Enrichment)
- 📋 CoreLogic market data integration
- 📋 Comparable property analysis
- 📋 AI-powered price suggestions
- 📋 Automated MLS listing generation

### Phase 3 (Planned - Agent Dashboard)
- 📋 Property management interface
- 📋 Listing text editor
- 📋 Analytics dashboard
- 📋 Shareable report link generation

### Phase 4 (Planned - Buyer Experience)
- 📋 Public property reports
- 📋 Interactive floor plan viewer
- 📋 Google Maps integration
- 📋 AI-powered Q&A chatbot

---

## 🏗 Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   React     │ ──────> │   Flask     │ ──────> │  Supabase   │
│  Frontend   │  HTTP   │   API       │  SQL    │  PostgreSQL │
└─────────────┘         └─────────────┘         └─────────────┘
                              │
                              │ Tasks
                              ↓
                        ┌─────────────┐         ┌─────────────┐
                        │   Celery    │ ──────> │   Redis     │
                        │   Workers   │  Queue  │   Broker    │
                        └─────────────┘         └─────────────┘
                              │
                              │ AI Calls
                              ↓
                    ┌──────────────────────┐
                    │   CrewAI Agents      │
                    │  1. Floor Plan       │
                    │  2. Market Analyst   │
                    │  3. Copywriter       │
                    └──────────────────────┘
                              │
                    ┌─────────┴─────────────┐
                    │                       │
              ┌─────▼─────┐         ┌─────▼─────┐
              │  Gemini   │         │ CoreLogic │
              │    LLM    │         │    API    │
              └───────────┘         └───────────┘
```

---

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 3.0 + Flask-CORS + Flask-JWT-Extended
- **Async Processing**: Celery 5.3 + Redis
- **AI Orchestration**: CrewAI 0.11
- **LLM**: Google Gemini 2.5 Flash
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **APIs**: CoreLogic Property API, Tavily Search, Google Maps

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: TailwindCSS 3.4
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest (backend), Jest (frontend)
- **Deployment**: Vercel (frontend), Heroku (backend)

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (20.10+) - [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (2.0+) - Included with Docker Desktop
- **Git** - [Download](https://git-scm.com/downloads)

Optional (for local development without Docker):
- Python 3.11+
- Node.js 20+
- Redis

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-floor-plan-insights
```

### 2. Configure Environment Variables

The `.env` file is already configured with your API keys. **Verify the file exists**:

```bash
cat .env
```

You should see all required environment variables populated.

### 3. Set Up Supabase Database

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to your project: `vuidefwnwsygxkzsjflv`
3. Open **SQL Editor**
4. Copy the contents of `backend/database_schema.sql`
5. Execute the script to create tables, indexes, and RLS policies
6. Go to **Storage** → Create bucket named `floor-plans` (private)

### 4. Build and Start Docker Containers

```bash
# Build all services
docker-compose build

# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services will be available at:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Redis: localhost:6379

### 5. Verify Installation

```bash
# Check service health
docker-compose ps

# Test backend health endpoint
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Floor Plan Insights API",
  "version": "1.0.0"
}
```

### 6. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:5000/docs (coming in Phase 1)

---

## 💻 Development Workflow

### Working on Backend

```bash
# Enter backend container
docker-compose exec backend bash

# Install new dependencies
pip install <package-name>
pip freeze > requirements.txt

# Run tests
pytest

# Check code style
black . --check
flake8
```

### Working on Frontend

```bash
# Enter frontend container
docker-compose exec frontend sh

# Install new dependencies
npm install <package-name>

# Run tests
npm test

# Lint code
npm run lint
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f frontend
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Rebuild after dependency changes
docker-compose up -d --build
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/unit/test_auth.py

# Run integration tests only
docker-compose exec backend pytest tests/integration/
```

### Frontend Tests

```bash
# Run all tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm run test:coverage

# Run in watch mode
docker-compose exec frontend npm test -- --watch
```

### Manual API Testing

Use the included test scripts:

```bash
# Test CoreLogic API
python backend/tests/manual/test_corelogic.py

# Test Gemini API
python backend/tests/manual/test_gemini.py
```

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new agent |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/auth/logout` | Logout current user |
| GET | `/auth/verify` | Verify JWT token |

### Property Endpoints (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/properties` | List all properties for agent |
| POST | `/api/properties/upload` | Upload floor plan |
| POST | `/api/properties/search` | Search by address |
| GET | `/api/properties/:id` | Get property details |
| PUT | `/api/properties/:id` | Update property |
| DELETE | `/api/properties/:id` | Delete property |

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/public/report/:token` | View public property report |
| POST | `/api/public/report/:token/log_view` | Log report view |
| POST | `/api/public/report/:token/chat` | Chat with property assistant |

**Full API documentation**: Coming in Phase 1 with Swagger UI

---

## 🔒 Security

This project follows **S.A.F.E. DRY principles** and implements OWASP Top 10 protections:

### Implemented Security Measures

- ✅ **Authentication**: JWT tokens with short expiration
- ✅ **Authorization**: Row Level Security (RLS) in Supabase
- ✅ **Secret Management**: Environment variables, never committed
- ✅ **CORS**: Configured for specific origins only
- ✅ **Input Validation**: All endpoints validate input
- ✅ **File Upload Security**: Type and size validation
- ✅ **Non-root Docker Users**: CIS Benchmark compliance

### Security Checklist for Production

- [ ] Change all default secret keys in `.env`
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure rate limiting on API
- [ ] Enable Supabase RLS policies
- [ ] Implement CSRF protection
- [ ] Add security headers (CSP, HSTS, etc.)
- [ ] Enable API request logging
- [ ] Configure WAF (Web Application Firewall)

---

## 📂 Project Structure

```
ai-floor-plan-insights/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── routes/              # API endpoints
│   │   ├── models/              # Database models
│   │   ├── services/            # Business logic
│   │   ├── agents/              # CrewAI agents
│   │   └── utils/               # Helper functions
│   ├── tests/
│   │   ├── unit/                # Unit tests
│   │   ├── integration/         # Integration tests
│   │   └── evaluation/          # AI agent tests
│   ├── requirements.txt
│   └── database_schema.sql
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── contexts/            # React contexts
│   │   ├── services/            # API clients
│   │   └── utils/               # Helper functions
│   ├── public/
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.celery
│   └── Dockerfile.frontend
├── docker-compose.yml
├── .env                         # Environment variables (gitignored)
├── .gitignore
├── plan.md                      # Development roadmap
├── log.md                       # Change tracking
└── README.md
```

---

## 🚢 Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Heroku)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create ai-floorplan-api

# Set environment variables
heroku config:set GOOGLE_GEMINI_API_KEY=<your-key>
# ... (set all env vars)

# Deploy
git push heroku main
```

### Database (Supabase)

Database is already hosted on Supabase Cloud. No deployment needed.

---

## 📖 Documentation

- **Development Plan**: See `plan.md` for detailed phase-by-phase roadmap
- **Change Log**: See `log.md` for all changes and decisions
- **Database Schema**: See `backend/database_schema.sql`
- **API Documentation**: Coming soon with Swagger UI

---

## 🤝 Contributing

This is a two-developer project:
- **Backend & Database**: You
- **Frontend**: Other developer

### Development Guidelines

1. Follow the phased plan in `plan.md`
2. Update `log.md` after each significant change
3. Write tests before implementing features (TDD)
4. Follow DRY principles - refactor duplicated code
5. Never commit `.env` or API keys
6. Use meaningful commit messages

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Troubleshooting

### Docker Issues

**Problem**: Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**Problem**: Port conflicts
```bash
# Check what's using the port
lsof -i :5000  # Backend
lsof -i :5173  # Frontend

# Change ports in docker-compose.yml if needed
```

### Database Issues

**Problem**: Can't connect to Supabase
```bash
# Verify environment variables
grep SUPABASE .env

# Test connection
python -c "from backend.app.utils.supabase_client import get_db; print(get_db())"
```

### API Key Issues

**Problem**: API calls failing
```bash
# Verify all keys are set
cat .env | grep API_KEY

# Test individual APIs
python backend/tests/manual/test_apis.py
```

---

## 📞 Support

For questions or issues:
1. Check `log.md` for known issues and solutions
2. Review `plan.md` for feature status
3. Check Docker logs: `docker-compose logs -f`
4. Create an issue in the repository

---

**Built with ❤️ following S.A.F.E. DRY A.R.C.H.I.T.E.C.T. principles**
