# 🔗 URL Shortener

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.5-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

Modern URL shortening service built with FastAPI and SQLite. Features a beautiful glassmorphism UI with animated backgrounds and real-time URL validation.

## ✨ Features

- 🚀 **Fast & Lightweight** - Built on FastAPI with SQLite
- 🎨 **Beautiful UI** - Glassmorphism design with animated gradients
- 🔒 **URL Validation** - Real-time accessibility checks
- 📊 **Click Tracking** - Monitor link performance
- 🎯 **Custom Aliases** - Create memorable short links
- 🔄 **Idempotent** - Same URL returns same short code
- ✅ **Well Tested** - 95%+ code coverage

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd url_shortener

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

Server will start at **http://localhost:8000**

### Run Tests

```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing tests/

# Expected coverage: ~95%
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/shorten` | Create a short URL |
| `GET` | `/{short_code}` | Redirect to original URL (302) |
| `GET` | `/api/info/{short_code}` | Get link statistics |
| `GET` | `/api/health` | Health check |
| `GET` | `/` | Web UI |

### API Examples

**Create Short URL:**
```bash
curl -X POST "http://localhost:8000/api/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**Create Custom Short URL:**
```bash
curl -X POST "http://localhost:8000/api/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "my-link"}'
```

**Get Link Info:**
```bash
curl "http://localhost:8000/api/info/my-link"
```

## 🏗️ Project Structure

```
url_shortener/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Configuration settings
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database connection
│   ├── crud.py           # Database operations
│   ├── routes.py         # API endpoints
│   ├── utils.py          # Helper functions
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── main.js
│   └── templates/
│       └── index.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_crud.py
│   └── test_utils.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🎨 UI Features

- **Glassmorphism Design** - Modern frosted glass effect
- **Animated Background** - Floating gradient blobs
- **Responsive Layout** - Works on all devices
- **Real-time Validation** - Instant feedback
- **Copy to Clipboard** - One-click copy functionality
- **Error Animations** - Smooth shake effects

## 🔧 Configuration

Create a `.env` file to customize settings:

```env
DATABASE_URL=sqlite:///./shortener.db
BASE_URL=http://localhost:8000
SHORT_CODE_LENGTH=6
```

## 🧪 Testing

The project includes comprehensive tests:

- **Unit Tests** - CRUD operations, utilities
- **Integration Tests** - API endpoints
- **Mocked External Calls** - URL accessibility checks

```bash
# Run specific test file
pytest tests/test_routes.py -v

# Run with coverage report
pytest --cov=app --cov-report=html tests/
```

## 📊 Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    clicks INTEGER DEFAULT 0
);

CREATE INDEX idx_short_code ON urls(short_code);
```

## 🔄 Migration to PostgreSQL

To switch from SQLite to PostgreSQL, simply update the `DATABASE_URL`:

```python
# .env
DATABASE_URL=postgresql://user:password@localhost/shortener
```

SQLAlchemy handles the rest automatically.

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **SQLite** - Lightweight database
- **Pytest** - Testing framework
- **HTTPX** - Async HTTP client
- **Jinja2** - Template engine

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

Made with ❤️ by [ternopolskiy](https://github.com/ternopolskiy)
