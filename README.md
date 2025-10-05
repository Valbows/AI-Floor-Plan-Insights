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

### Phase 0: Foundation ✅ COMPLETE
- ✅ Docker-based development environment
- ✅ Flask REST API with JWT authentication
- ✅ React frontend with mobile-first design
- ✅ Supabase database with Row Level Security
- ✅ Celery async task processing with Redis

### Phase 1: Data Ingestion ✅ COMPLETE
- ✅ Floor plan image upload with validation
- ✅ AI-powered floor plan parsing (Gemini Vision)
- ✅ Room detection and feature extraction
- ✅ Square footage estimation
- ✅ User authentication system (JWT)
- ✅ Real-time status updates

### Phase 2: AI Enrichment ✅ COMPLETE
- ✅ CoreLogic API integration (OAuth2)
- ✅ Comparable property analysis
- ✅ AVM (Automated Valuation Model)
- ✅ AI-powered market insights (Agent #2)
- ✅ Investment scoring and rental estimates
- ✅ Automated MLS listing generation (Agent #3)
- ✅ Social media content creation (4 platforms)
- ✅ SEO keyword optimization
- ✅ Complete 3-agent workflow pipeline

### Phase 3: Agent Dashboard (In Progress)
- 🔨 Property management interface
- 🔨 Market insights visualization
- 🔨 Listing copy display and editor
- 🔨 Social media preview/sharing
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
                    │   AI Agents (Gemini) │
                    │  #1 Floor Plan       │
                    │  #2 Market Analyst   │
                    │  #3 Copywriter       │
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
- **Async Processing**: Celery 5.3 + Redis 7.2
- **AI Models**: Google Gemini 2.0 Flash (Vision + Text)
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **APIs**: CoreLogic Property API (OAuth2), Google Gemini API
- **Structured Output**: Pydantic 2.0 for schema validation

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

Create a `.env` file in the project root with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# JWT Secret
JWT_SECRET_KEY=your-secure-random-key

# Google Gemini API
GOOGLE_GEMINI_API_KEY=your-gemini-api-key

# CoreLogic API (Required for Phase 2 - Market Insights)
CORELOGIC_CONSUMER_KEY=your-consumer-key
CORELOGIC_CONSUMER_SECRET=your-consumer-secret

# Flask Configuration
FLASK_ENV=development
```

**Note**: Without CoreLogic credentials, Agent #2 will use fallback logic (square footage-based estimates).

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
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

**Default Login Credentials**:
- Email: `jane.smith@realestate.com`
- Password: `Agent2025!`

### 7. (Optional) Add CoreLogic API Credentials

For real market data from Agent #2 (Market Insights Analyst):

1. **Get API Credentials**:
   - Sign up at [CoreLogic Developer Portal](https://developer.corelogic.com/)
   - Request access to Property API
   - Obtain Consumer Key and Consumer Secret

2. **Update `.env` file**:
   ```bash
   CORELOGIC_CONSUMER_KEY=your_real_key
   CORELOGIC_CONSUMER_SECRET=your_real_secret
   ```

3. **Restart services**:
   ```bash
   docker-compose restart backend celery-worker
   ```

**Without CoreLogic**: Agent #2 uses fallback logic (~$200/sqft estimates)
**With CoreLogic**: Agent #2 provides real comps, AVM, and market trends

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

### Phase 2 Workflow Test (3-Agent Pipeline)

Test the complete workflow: Upload → Agent #1 → Agent #2 → Agent #3

```bash
# Automated test script (recommended)
python3 test_phase2_workflow.py

# Expected output:
# ✓ Login successful!
# ✓ Upload successful!
# ✓ Workflow complete in 30-60 seconds!
# ✓ All 3 agents executed successfully!
```

**Manual testing via curl**:
```bash
# See TEST_COMMANDS.md for detailed curl examples
cat TEST_COMMANDS.md
```

**Monitor Celery logs in real-time**:
```bash
docker logs -f ai-floorplan-celery
```

### Backend Unit Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run CoreLogic client tests
docker-compose exec backend pytest backend/tests/unit/test_corelogic_client.py -v

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

## 🤖 AI Agent Workflow (Phase 2)

### Complete 3-Agent Pipeline

The system uses a sequential AI agent workflow powered by Google Gemini:

```
1️⃣ UPLOAD FLOOR PLAN + ADDRESS
         ↓
🤖 Agent #1: Floor Plan Analyst (Gemini Vision)
   └─ Analyzes image to extract:
      • Bedrooms, bathrooms, square footage
      • Room types and dimensions
      • Features (balcony, walk-in closet, etc.)
      • Layout type (Traditional, Open Concept, etc.)
   └─ Status: processing → parsing_complete (~5-10s)
         ↓
🤖 Agent #2: Market Insights Analyst (Gemini + CoreLogic)
   └─ Fetches CoreLogic data:
      • Comparable properties within 1 mile
      • AVM (Automated Valuation Model)
      • Property history and characteristics
   └─ AI Analysis generates:
      • Price estimate with confidence level
      • Value range (low-high)
      • Market trend (rising/stable/declining)
      • Investment score (1-100)
      • Rental income estimates
      • Cap rate for investors
      • Risk factors and opportunities
   └─ Status: parsing_complete → enrichment_complete (~15-30s)
         ↓
🤖 Agent #3: Listing Copywriter (Gemini)
   └─ Uses data from Agent #1 & #2 to generate:
      • Attention-grabbing headline (60 chars)
      • MLS-ready description (500-800 words)
      • Key highlights (5-8 bullet points)
      • Compelling call-to-action
      • Social media captions (Instagram, Facebook, Twitter, LinkedIn)
      • Email subject line
      • SEO keywords (8-12 keywords)
   └─ Customizable tone: professional, luxury, family, investor, modern
   └─ Status: enrichment_complete → complete (~10-20s)
         ↓
✅ COMPLETE PROPERTY PACKAGE
   └─ Floor plan analysis
   └─ Market valuation and insights
   └─ Professional listing copy
   └─ Social media content
   └─ Total time: 30-60 seconds
```

**All data stored in single JSONB column** (`extracted_data`) for maximum flexibility.

**Fallback Logic**: If CoreLogic API is unavailable, Agent #2 uses square footage-based estimates (~$200/sqft) with clearly marked low confidence.

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
