# BRIN Research Explorer

Platform analisis publikasi ilmiah Indonesia dengan topic modeling dan visualisasi data interaktif.

## 🎯 Overview

BRIN Research Explorer adalah sistem untuk mengumpulkan, menganalisis, dan memvisualisasikan publikasi riset Indonesia dari berbagai institusi nasional (BRIN, universitas, dll). Platform ini menggunakan **topic modeling** untuk mengidentifikasi tren riset secara otomatis.

## ✨ Features

- 🔍 **Data Collection**: Automated fetching dari OpenAlex API
- 🤖 **Topic Modeling**: LDA algorithm untuk identifikasi topik riset
- 📊 **Analytics**: Statistik publikasi, peneliti, dan institusi
- 🔎 **Search & Filter**: Cari berdasarkan judul, tahun, topik, institusi
- 📈 **Trend Analysis**: Visualisasi tren riset dari tahun ke tahun
- 🌐 **REST API**: Endpoints untuk integrasi frontend

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  OpenAlex   │ ───> │   FastAPI    │ ───> │ PostgreSQL  │
│     API     │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Topic Model  │
                     │    (LDA)     │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Frontend    │
                     │  Dashboard   │
                     └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip/virtualenv

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd brin-research-explorer/backend
```

2. **Setup virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
```bash
# Edit .env file
DATABASE_URL=postgresql://user:password@localhost:5432/brin_research_db
```

5. **Initialize database**
```bash
python scripts/init_database.py
```

6. **Run backend**
```bash
cd app
uvicorn main:app --reload
```

API available at: `http://localhost:8000`

### Fetch Data

```bash
# Fetch Indonesian research publications
python scripts/fetch_national_data.py --limit 500 --email your@email.com

# Or seed sample data
python scripts/seed_data.py
```

## 📊 Current Data

- **497 publications** (2020-2024)
- **2,059 researchers**
- **12 research topics**
- **Coverage**: BRIN, UI, ITB, UGM, ITS, UNAIR, etc.

## 🔧 Tech Stack

**Backend:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Scikit-learn - Machine learning (LDA)
- Pandas, NumPy - Data processing

**Data Source:**
- OpenAlex API

## 📖 API Documentation

Visit `/docs` after running the backend for interactive API documentation (Swagger UI).

**Main Endpoints:**
- `GET /api/publications` - List publications (with pagination)
- `GET /api/publications/{id}` - Get publication detail
- `GET /api/publications/stats` - Get statistics
- `GET /api/topics` - List topics
- `GET /api/topics/trends` - Topic trends over time

## 🗂️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/                 # API endpoints
│   └── services/            # Business logic
├── scripts/                 # Utility scripts
└── tests/                   # Unit tests
```

## 🔮 Future Development

- [ ] Frontend dashboard (React)
- [ ] Real-time collaboration network visualization
- [ ] Citation impact analysis
- [ ] Export to PDF/CSV
- [ ] Scheduled data updates
- [ ] Advanced filtering & search

## 👨‍💻 Author

Developed by Septian Samdani

## 📝 License

MIT License

## 🙏 Acknowledgments

- OpenAlex for providing open research data
- BRIN for internship opportunity