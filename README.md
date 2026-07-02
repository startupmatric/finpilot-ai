# FinPilot - AI-Powered Financial Analytics Platform

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1A1A2E?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge&logo=groq&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

<div align="center">
<h3>💰 Your AI-Powered Financial Co-Pilot</h3>
<p><em>Upload, Analyze, and Optimize Your Finances with Intelligence</em></p>
<p>
<a href="#-features">Features</a> •
<a href="#-architecture">Architecture</a> •
<a href="#-tech-stack">Tech Stack</a> •
<a href="#-quick-start">Quick Start</a> •
<a href="#-api-reference">API Reference</a>
</p>
<p>
<img src="https://img.shields.io/github/stars/startupmatric/finpilot?style=social" alt="GitHub stars"/>
<img src="https://img.shields.io/github/forks/startupmatric/finpilot?style=social" alt="GitHub forks"/>
</p>
</div>

## 📖 Table of Contents
- [About](#-about)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [AI Workflow](#-ai-workflow)
- [Screenshots](#-screenshots)
- [API Reference](#-api-reference)
- [Folder Structure](#-folder-structure)
- [Quick Start](#-quick-start)
- [Roadmap](#-roadmap)
- [License](#-license)

## 🚀 About

FinPilot is a production-ready financial analytics platform that combines traditional data analysis with modern AI capabilities. It helps individuals and businesses:

- 📊 Track spending with intelligent categorization
- 🤖 Get AI-powered insights through natural language chat
- 📈 Forecast future spending using statistical analysis
- 💰 Monitor budgets with real-time tracking
- 🔄 Detect subscriptions and recurring payments
- 💚 Measure financial health with a comprehensive score

Unlike basic expense trackers, FinPilot uses a multi-agent AI system powered by LangGraph and Groq LLM to provide personalized financial coaching and insights.

## ✨ Features

### 📤 Data Ingestion
- **CSV Upload**: Import bank statements and transaction history
- **Validation**: Automatic data validation with detailed error reporting
- **Categorization**: Rule-based and AI-powered transaction categorization

### 📊 Analytics Engine
- **Spending Analysis**: Breakdown by category, merchant, and time
- **Statistical Insights**: Mean, median, standard deviation, trends
- **Merchant Analysis**: Top merchants, spending history, patterns
- **Monthly Trends**: Month-over-month growth and comparisons

### 🎯 Smart Features
- **Financial Health Score**: 0-100 score based on spending patterns
- **Budget Tracking**: Real-time budget monitoring with alerts
- **Subscription Detection**: Automatic identification of recurring payments
- **Forecast Engine**: Statistical predictions for future spending

### 🤖 AI Assistant
- **Natural Language Chat**: Ask questions about your finances
- **Multi-Agent System**: Specialized agents for spending, merchants, budget, and coaching
- **Personalized Insights**: AI-powered recommendations and action plans
- **Context-Aware**: Remembers previous conversations for better responses

### 🔐 Security
- **JWT Authentication**: Secure user authentication and authorization
- **Multi-Tenant**: Each user has isolated data
- **Password Hashing**: bcrypt encryption for passwords
- **CORS**: Configurable cross-origin resource sharing

## 🏗️ Architecture

![Uploading image.png…]()


## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | Modern, fast web framework for building APIs |
| SQLAlchemy 2.0 | ORM for PostgreSQL database interactions |
| PostgreSQL | Production-ready relational database |
| Pydantic | Data validation and serialization |
| python-jose | JWT authentication |
| passlib | Password hashing (bcrypt) |

### AI & ML
| Technology | Purpose |
|---|---|
| LangGraph | Multi-agent orchestration framework |
| Groq | High-performance LLM API (Llama 3.1) |
| LangChain | Framework for building LLM applications |
| Pandas | CSV parsing and data manipulation |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5/CSS3 | Structure and styling |
| Chart.js | Interactive data visualizations |
| Axios | HTTP client for API calls |
| Vanilla JS | Clean, framework-free JavaScript |

### DevOps
| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Uvicorn | ASGI server for FastAPI |
| Git | Version control |

## 🤖 AI Workflow

The AI system uses a multi-agent architecture with LangGraph:

```
![Uploading image.png…]()

```

**Key AI Features:**
- **Tool Calling**: LLM selects the right analytics tool automatically
- **Multi-Agent**: Specialized agents for different tasks
- **Memory**: Context-aware conversations
- **Deterministic Data**: LLM only explains verified data — never calculates

## 📸 Screenshots

> TODO: Replace with real screenshots once the dark/metallic-gold dashboard styling is finalized.

**Dashboard** — Comprehensive dashboard with spending overview, charts, and health score
`assets/screenshots/dashboard.png`

**AI Chat** — Natural language interface for financial queries
`assets/screenshots/chat.png`

**Analytics** — Detailed analytics with category breakdown and merchant analysis
`assets/screenshots/analytics.png`

**Forecast** — Statistical forecasting for future spending
`assets/screenshots/forecast.png`

**Budget Tracking** — Real-time budget monitoring with visual indicators
`assets/screenshots/budget.png`

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user info |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/transactions` | List transactions (with filters) |
| GET | `/api/v1/transactions/{id}` | Get single transaction |
| GET | `/api/v1/categories` | Get all categories |

### Upload
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/upload` | Upload CSV file |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/spending/total` | Total spending |
| GET | `/api/v1/analytics/spending/category` | Category breakdown |
| GET | `/api/v1/analytics/spending/daily` | Daily spending |
| GET | `/api/v1/analytics/spending/monthly` | Monthly spending |
| GET | `/api/v1/analytics/merchant/top` | Top merchants |
| GET | `/api/v1/analytics/merchant/{name}/total` | Merchant total |
| GET | `/api/v1/analytics/merchant/{name}/history` | Merchant history |
| GET | `/api/v1/analytics/statistics` | Transaction statistics |
| GET | `/api/v1/analytics/budget` | Budget status |
| GET | `/api/v1/analytics/health` | Health score |
| GET | `/api/v1/analytics/coach/weekly` | Weekly coaching report |
| GET | `/api/v1/analytics/subscriptions` | Detect subscriptions |
| GET | `/api/v1/analytics/forecast/monthly` | Monthly forecast |
| GET | `/api/v1/analytics/forecast/cashflow` | Cashflow forecast |

### AI Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat` | Send AI query |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc documentation |

## 📁 Folder Structure

```
finpilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── upload.py          # CSV upload endpoint
│   │   │       ├── transactions.py    # Transaction CRUD
│   │   │       ├── analytics.py       # Analytics endpoints
│   │   │       ├── chat.py            # AI Chat endpoint
│   │   │       └── auth.py            # Authentication endpoints
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                 # JWT handling
│   │   │   ├── security.py            # Password hashing
│   │   │   └── dependencies.py        # Auth dependencies
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── database.py            # SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py         # Transaction model
│   │   │   └── user.py                # User model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py         # Pydantic schemas
│   │   │   └── analytics.py           # Analytics schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── csv_import.py          # CSV parsing
│   │   │   ├── validator.py           # Data validation
│   │   │   ├── categorizer.py         # Rule-based categorization
│   │   │   ├── coach_service.py       # Financial coaching
│   │   │   ├── subscription_service.py # Subscription detection
│   │   │   ├── forecast_service.py    # Forecasting engine
│   │   │   └── analytics/             # Analytics services
│   │   │       ├── spending.py
│   │   │       ├── merchant.py
│   │   │       ├── monthly.py
│   │   │       ├── budget.py
│   │   │       ├── health_score.py
│   │   │       └── statistics.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── supervisor.py          # LangGraph supervisor
│   │   │   ├── spending_agent.py
│   │   │   ├── merchant_agent.py
│   │   │   ├── budget_agent.py
│   │   │   ├── statistics_agent.py
│   │   │   └── coach_agent.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── state.py               # Shared state
│   │   │   ├── nodes.py               # Graph nodes
│   │   │   └── workflow.py            # LangGraph workflow
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── groq_client.py         # Groq API client
│   │   │   └── prompts.py             # System prompts
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── analytics_tools.py     # Analytics tools
│   │   │   └── transaction_tools.py   # Transaction tools
│   │   ├── config.py                  # App configuration
│   │   └── main.py                    # FastAPI entry point
│   ├── data/
│   │   └── sample.csv                 # Sample transaction data
│   ├── .env                           # Environment variables
│   └── requirements.txt               # Python dependencies
│
├── frontend/
│   ├── index.html                     # Main HTML
│   ├── css/
│   │   └── styles.css                 # Styles
│   └── js/
│       └── app.js                     # Frontend logic
│
├── docker-compose.yml                 # Docker configuration
├── Dockerfile                         # Backend Dockerfile
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for frontend development)
- Groq API Key ([Get one here](https://console.groq.com))

### Backend Setup

**1. Clone the Repository**
```bash
git clone https://github.com/startupmatric/finpilot.git
cd finpilot/backend
```

**2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

`.env` Example:
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/finpilot

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Application
DEBUG=True
APP_NAME=FinPilot
APP_VERSION=0.1.0
```

**5. Setup Database**
```bash
# Create database
psql -U postgres -c "CREATE DATABASE finpilot;"

# Run migrations (auto-creates tables on startup)
python -m uvicorn app.main:app --reload
```

**6. Run Backend**
```bash
python -m uvicorn app.main:app --reload
```
The API will be available at: `http://localhost:8000`

### Frontend Setup

**1. Serve Frontend**
```bash
cd frontend
python -m http.server 3000
# Or use VS Code Live Server extension
```
The dashboard will be available at: `http://localhost:3000`

### Docker Setup (Alternative)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🗺️ Roadmap

### Phase 1: Core Backend ✅
- FastAPI REST API
- PostgreSQL database
- CSV upload with validation
- Transaction management
- Analytics engine
- JWT authentication

### Phase 2: AI Integration ✅
- LangGraph multi-agent system
- Groq LLM integration
- Natural language chat
- Financial coaching
- Intent routing

### Phase 3: Smart Features ✅
- Budget tracking
- Health score
- Subscription detection
- Forecasting engine
- Weekly reports

### Phase 4: Frontend ✅
- Modern dashboard
- Interactive charts
- AI chat interface
- Transaction management
- Budget visualization

### Phase 5: Production (In Progress)
- Advanced caching (Redis)
- Background jobs (Celery)
- Email notifications
- Mobile responsive design
- Performance optimization

### Phase 6: Enterprise Features (Future)
- Multi-currency support
- Export reports (PDF/Excel)
- Webhooks and integrations
- API rate limiting
- Admin dashboard

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read the Contributing Guide for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- FastAPI for the web framework
- LangChain for the AI orchestration
- Groq for the LLM API
- Chart.js for the charting library
- All open-source contributors whose work made this possible

## 📞 Contact

**Project Lead:** Yashwanth
**GitHub:** [@startupmatric](https://github.com/startupmatric)
**LinkedIn:** [yashwanth-s072003](https://linkedin.com/in/yashwanth-s072003)
**Email:** TODO — add your email

<div align="center">
<strong>⭐ If you like this project, give it a star! ⭐</strong>
<br><br>
<sub>Built with ❤️ by Yashwanth</sub>
</div>
