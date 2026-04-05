# ⬡ ProcureIQ
### Autonomous Procurement Intelligence System

> **Multi-agent AI system that autonomously discovers suppliers, negotiates prices, assesses risk, forecasts markets, and generates procurement documents — with human-in-the-loop approval.**

<br>

![ProcureIQ Dashboard](https://img.shields.io/badge/Status-Live-00c853?style=for-the-badge&logo=railway)
![Python](https://img.shields.io/badge/Python-3.11-FF0000?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-FF0000?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF0000?style=for-the-badge&logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF0000?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-FF0000?style=for-the-badge&logo=postgresql&logoColor=white)

---

## 🎯 What Is ProcureIQ?

ProcureIQ is a fully autonomous procurement intelligence platform powered by a **multi-agent AI pipeline**. A user submits a procurement request (e.g. *"500 industrial sensors, ₹250,000 budget"*) and the system autonomously:

1. **Discovers** real suppliers using live web search
2. **Scores** each supplier for risk using ML
3. **Forecasts** price trends using time-series analysis
4. **Negotiates** strategy using LLM reasoning
5. **Drafts** RFQ, contract, and purchase order documents
6. **Notifies** a human approver via email
7. **Awaits** human approval before finalizing
8. **Generates** final procurement documents on approval

All of this happens in **20–30 seconds**, end-to-end.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                    │
│         (Hugging Face Spaces — Private)                  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP + API Key
┌───────────────────────▼─────────────────────────────────┐
│                   FASTAPI BACKEND                        │
│              (Railway — procureiq-production)            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              LANGGRAPH PIPELINE                  │    │
│  │                                                  │    │
│  │  Supplier      Risk        Price       Decision  │    │
│  │  Discovery ──► Scoring ──► Intel ──►  Engine    │    │
│  │     │                                    │       │    │
│  │  Negotiation   RFQ Gen   Contract    Email Notif │    │
│  │  Strategy  ──► erator ──► Drafter ──► ication   │    │
│  │                                                  │    │
│  │              [HUMAN APPROVAL]                    │    │
│  │                    │                             │    │
│  │              PO Generation                       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  PostgreSQL (Railway)    Redis    Resend Email API       │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Pipeline

| Agent | Role | Technology |
|-------|------|------------|
| **Supplier Discovery** | Searches web for real suppliers with prices | DuckDuckGo Search + Groq LLM |
| **Risk Scoring** | ML-based supplier risk assessment | scikit-learn |
| **Price Intelligence** | 30/60/90 day price forecasting | NumPy linear regression |
| **Decision Engine** | Buy / Wait / Escalate decision | LangGraph + Groq LLM |
| **Negotiation Strategist** | Generates negotiation tactics | Groq LLM |
| **RFQ Generator** | Drafts Request for Quotation | FPDF2 |
| **Contract Drafter** | Generates procurement contract | FPDF2 |
| **Email Notifier** | Sends approval request email | Resend API |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — REST API with API key authentication
- **LangGraph** — Multi-agent workflow orchestration
- **LangChain + Groq** — LLM reasoning (Llama 3)
- **CrewAI** — Agent coordination
- **SQLAlchemy + PostgreSQL** — Persistent storage
- **Redis** — State caching
- **FPDF2** — Document generation
- **DuckDuckGo Search** — Real-time supplier discovery
- **Resend** — Email notifications

### Frontend
- **Streamlit** — Interactive dashboard
- **Custom CSS** — Dark theme with animated KPI cards

### Infrastructure
- **Railway** — Backend + PostgreSQL hosting
- **Hugging Face Spaces** — Frontend hosting
- **GitHub** — Private repository + CI/CD

---

## 🚀 Features

- ✅ **Autonomous multi-agent pipeline** — zero manual steps
- ✅ **Real supplier discovery** — live web search, not mock data
- ✅ **ML risk scoring** — per-supplier risk assessment
- ✅ **Price forecasting** — 30/60/90 day trend analysis
- ✅ **Human-in-the-loop** — approval gate before PO generation
- ✅ **Email notifications** — rich HTML approval emails
- ✅ **Document generation** — PO, RFQ, Contract PDFs
- ✅ **Full audit trail** — every agent action logged
- ✅ **Persistent database** — PostgreSQL on Railway
- ✅ **Live deployment** — production-ready on Railway + HuggingFace

---

## 📸 Screenshots

### Dashboard
![Dashboard](https://github.com/user-attachments/assets/ff667ae3-0179-4747-8f4d-73b4de278483)

### Email Notification — Approval Request
![Email 1](https://github.com/user-attachments/assets/87de64bb-0bf0-4031-9cd1-5ade6c879d75)
![Email 2](https://github.com/user-attachments/assets/988b029b-8239-43f7-9ef0-2f112fb219fe)

### Documents Tab
![Documents 1](https://github.com/user-attachments/assets/fbb557bb-6fc4-4fac-879b-f930ceacfbf6)
![Documents 2](https://github.com/user-attachments/assets/0220d52d-5827-45e1-bce8-8ddcc37e0d61)

---

## 🔧 Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for local dev)
- Redis (optional)

### Installation

```bash
# Clone the repo
git clone https://github.com/manunaik111/procureiq.git
cd procureiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
# API
API_KEY=your-secret-key

# LLM
GROQ_API_KEY=your-groq-api-key

# Email
RESEND_API_KEY=your-resend-api-key
GMAIL_ADDRESS=your@gmail.com

# Database (leave blank to use SQLite locally)
DATABASE_URL=

# Redis (optional)
REDIS_URL=
USE_REDIS_SAVER=false
```

### Run

```bash
# Start backend
python main.py

# Start frontend (in a new terminal)
streamlit run dashboard/app.py
```

---

## 🌐 Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Backend API | Railway | `procureiq-production-8df0.up.railway.app` |
| Frontend | Hugging Face Spaces | Private |
| Database | Railway PostgreSQL | Internal |

### API Endpoints

```
POST /procure          — Start autonomous procurement
POST /approve/{id}     — Approve and generate documents  
GET  /status/{id}      — Get procurement status
GET  /health           — Health check
```

---

## 📊 How It Works — Step by Step

```
User submits request
        │
        ▼
[Supplier Discovery Agent]
 Searches web for real suppliers
 Extracts prices, URLs, contact info
        │
        ▼
[Risk Scoring Agent]
 ML model scores each supplier
 Factors: price variance, domain age, etc.
        │
        ▼
[Price Intelligence Agent]
 Generates 365-day price history
 Forecasts 30/60/90 day prices
 Determines trend: rising/falling/stable
        │
        ▼
[Decision Engine]
 Analyzes all data
 Decision: BUY / WAIT / ESCALATE
        │
        ▼
[Negotiation Strategist]
 Generates negotiation tactics
 Based on supplier risk + price trend
        │
        ▼
[Document Generator]
 Drafts RFQ + Contract
        │
        ▼
[Email Notifier]
 Sends rich HTML email to approver
 Includes: supplier, risk, forecast, audit trail
        │
        ▼
[HUMAN APPROVAL] ◄─── Human reviews and approves
        │
        ▼
[PO Generator]
 Generates final Purchase Order
 Saves to PostgreSQL
 Updates dashboard
```

---

## 🧠 Why I Built This

Procurement is one of the most manual, time-consuming business processes. Companies spend weeks getting quotes, evaluating suppliers, and generating documents. I wanted to explore whether a multi-agent AI system could compress that to **under a minute** while maintaining human oversight at the critical decision point.

This project pushed me to integrate:
- Complex multi-agent orchestration with LangGraph
- Real-time web scraping for supplier data
- ML-based risk assessment
- Production deployment across multiple platforms
- Human-in-the-loop workflow design

---

## 👤 Author

**Manu Naik**  
[GitHub](https://github.com/manunaik111)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built with ⬡ by Manu Naik</strong><br>
  <em>Autonomous · Multi-Agent · Real-Time</em>
</div>
