# 🔗 Gosha Connections Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.5-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-8.3-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

A modern, full-featured URL shortener platform inspired by Bitly. Built with FastAPI, featuring analytics, QR codes, bio pages, and a beautiful responsive UI with dark mode support.

---

## 📚 Documentation & Design

<div align="center">

### 🎨 UI/UX Design & Specifications

[![Figma Mockups](https://img.shields.io/badge/Figma-UI_Mockups-F24E1E?style=for-the-badge&logo=figma&logoColor=white)](https://www.figma.com/design/MWhmrUY7hnuCvIzPTRGFmv/INT_POLE?node-id=0-1&t=0htrnVfHJW1NSZyr-1)
[![Google Docs](https://img.shields.io/badge/Google_Docs-Control_Elements-4285F4?style=for-the-badge&logo=googledocs&logoColor=white)](https://docs.google.com/document/d/1X6Tsr8KPmO38-qIC8dQoZ9GD3sq8ItiZUVzt4w_N4iI/edit?tab=t.0)

**📐 Figma Mockups** — Complete UI/UX design and interface mockups  
**🎛️ Control Elements** — Detailed button functionality and interaction specifications

</div>

---

## 🗺️ Navigation Map

<div align="center">
  
### Complete Site Structure Visualization

![Navigation Map](image_homework/ВЕРОНИЧКА.drawio.svg)

</div>

---

## ✨ Features

### 🔗 Core Features
- **URL Shortening** — Create short links with custom codes or auto-generated ones
- **Link Management** — Full CRUD operations with search and filtering
- **Custom Short Codes** — Use your own memorable short codes
- **Link Expiration** — Set expiration dates for temporary links
- **Active/Inactive Toggle** — Enable or disable links without deletion

### 📊 Analytics & Tracking
- **Click Analytics** — Track every click with detailed metadata
- **Device Detection** — Browser, OS, and device type tracking
- **Geographic Data** — Country and city information (IP-based)
- **Referrer Tracking** — See where your traffic comes from
- **Time-based Charts** — Visualize clicks over time
- **Activity Heatmap** — GitHub-style contribution calendar

### 👤 User Management
- **Authentication System** — Secure JWT-based auth with httpOnly cookies
- **User Registration** — Email and username validation
- **Profile Management** — Update username, email, password
- **Avatar Upload** — Custom profile pictures (JPG, PNG, GIF, WebP)
- **Theme Preferences** — Light/Dark mode with system sync
- **Multi-language Support** — English, Russian, Spanish, French, German
- **Account Deletion** — Self-service account deletion with password confirmation

### 🛡️ Admin Panel
- **Platform Statistics** — Total users, links, clicks with growth metrics
- **User Management** — View, activate/deactivate, and delete users
- **Link Management** — Monitor and delete any link on the platform
- **Activity Dashboard** — Visual charts showing platform activity over time
- **Search & Filter** — Find users and links quickly
- **Role-based Access** — Admin-only protected routes

### 🎨 User Interface
- **Modern Design** — Clean, professional interface inspired by Bitly
- **Dark Mode** — Beautiful dark theme with smooth transitions
- **Responsive Layout** — Works perfectly on mobile, tablet, and desktop
- **Toast Notifications** — User-friendly feedback for all actions
- **Loading States** — Smooth loading indicators and animations
- **Accessibility** — Semantic HTML and keyboard navigation support

### 🔐 Security
- **Password Hashing** — Bcrypt for secure password storage
- **JWT Tokens** — Access and refresh token system
- **HttpOnly Cookies** — Secure token storage
- **CORS Protection** — Configurable CORS middleware
- **SQL Injection Prevention** — SQLAlchemy ORM protection
- **XSS Protection** — Template escaping and sanitization

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ternopolskiy/url_shortener.git
cd url-shortener
```

2. **Create virtual environment** (recommended)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the application**

Open your browser and navigate to: **http://localhost:8000**

### First Launch

On first startup, the application will automatically:
- ✅ Create the SQLite database (`gosha.db`)
- ✅ Initialize all database tables
- ✅ Run necessary migrations
- ✅ Create an admin account

### Default Admin Credentials

```
Email: admin@gosha.link
Password: Admin123!
```

**⚠️ Important:** Change the admin password immediately after first login!

You can customize admin credentials in `app/config.py` or via environment variables.

## 📁 Project Structure

```
url-shortener/
├── app/
│   ├── api/                      # API route handlers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── links.py             # Link management endpoints
│   │   ├── users.py             # User profile endpoints
│   │   ├── analytics.py         # Analytics endpoints
│   │   ├── admin.py             # Admin panel endpoints
│   │   └── redirect.py          # Short URL redirect handler
│   ├── core/                     # Core functionality
│   │   ├── security.py          # JWT, password hashing
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── exceptions.py        # Custom exceptions
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   ├── variables.css    # CSS custom properties (themes)
│   │   │   ├── base.css         # Base styles
│   │   │   ├── components.css   # Reusable components
│   │   │   └── style.css        # Additional styles
│   │   ├── js/
│   │   │   ├── theme.js         # Theme switcher
│   │   │   ├── app.js           # Common utilities
│   │   │   └── main.js          # Main application logic
│   │   └── uploads/             # User uploads (avatars)
│   ├── templates/                # Jinja2 templates
│   │   ├── auth/                # Authentication pages
│   │   ├── dashboard/           # User dashboard pages
│   │   ├── admin/               # Admin panel pages
│   │   ├── public/              # Public pages
│   │   ├── components/          # Reusable components
│   │   └── base.html            # Base layout template
│   ├── config.py                # Application configuration
│   ├── database.py              # SQLAlchemy setup
│   ├── models.py                # Database models
│   ├── schemas.py               # Pydantic schemas
│   ├── utils.py                 # Utility functions
│   └── main.py                  # FastAPI application
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest configuration
│   ├── test_routes.py           # Route tests
│   ├── test_crud.py             # CRUD operation tests
│   └── test_utils.py            # Utility function tests
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── run.py                        # Application runner
└── README.md                     # This file
```

## 🗄️ Database Schema

The application uses SQLite with the following tables:

### Users Table
- User authentication and profile data
- Roles: `user`, `admin`
- Theme and language preferences
- Avatar URLs

### URLs Table
- Short links with custom or auto-generated codes
- Original URL, title, tags
- Active status and expiration dates
- Click count tracking

### Clicks Table
- Detailed click analytics
- IP address, user agent, referer
- Device type, browser, OS
- Geographic data (country, city)
- Timestamp for time-based analysis

### QR Codes Table
- QR code configurations
- Custom colors and styles
- Logo support

### Bio Pages Table
- Personal landing pages
- Custom slugs and themes
- View count tracking

### Bio Links Table
- Links on bio pages
- Custom icons and positioning
- Click tracking

## 🔐 Authentication Flow

The platform uses a secure JWT-based authentication system:

1. **Registration/Login** → Server generates JWT tokens
2. **Access Token** (30 min) → Stored in httpOnly cookie
3. **Refresh Token** (7 days) → Stored in httpOnly cookie
4. **Auto-refresh** → Seamless token renewal when access token expires
5. **Logout** → Cookies cleared, tokens invalidated

### Security Features
- Passwords hashed with bcrypt
- HttpOnly cookies prevent XSS attacks
- CSRF protection via SameSite cookies
- Secure flag for HTTPS in production

## 📡 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| POST | `/api/v1/auth/logout` | Logout user | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |

### Link Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/links` | Create short link | Yes |
| GET | `/api/v1/links` | Get user's links | Yes |
| GET | `/api/v1/links/{id}` | Get link details | Yes |
| PATCH | `/api/v1/links/{id}` | Update link | Yes |
| DELETE | `/api/v1/links/{id}` | Delete link | Yes |

### User Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users/me/stats` | Get user statistics | Yes |
| PATCH | `/api/v1/users/me` | Update profile | Yes |
| PATCH | `/api/v1/users/me/password` | Change password | Yes |
| PATCH | `/api/v1/users/me/theme` | Update theme | Yes |
| PATCH | `/api/v1/users/me/language` | Update language | Yes |
| POST | `/api/v1/users/me/avatar` | Upload avatar | Yes |
| DELETE | `/api/v1/users/me/avatar` | Delete avatar | Yes |
| DELETE | `/api/v1/users/me` | Delete account | Yes |
| GET | `/api/v1/users/me/activity` | Get activity heatmap | Yes |

### Analytics Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/analytics/links/{id}` | Get link analytics | Yes |
| GET | `/api/v1/analytics/links/{id}/chart` | Get click chart data | Yes |

### Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/admin/stats` | Platform statistics | Admin |
| GET | `/api/v1/admin/users` | List all users | Admin |
| PATCH | `/api/v1/admin/users/{id}` | Update user | Admin |
| DELETE | `/api/v1/admin/users/{id}` | Delete user | Admin |
| GET | `/api/v1/admin/links` | List all links | Admin |
| DELETE | `/api/v1/admin/links/{id}` | Delete link | Admin |
| GET | `/api/v1/admin/activity` | Platform activity | Admin |

### Redirect Endpoint

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/{short_code}` | Redirect to original URL | No |

## 🎨 Design System

### Color Palette

**Light Theme:**
- Background: `#FFFDF8` (Warm white)
- Surface: `#FFFFFF` (Pure white)
- Primary: `#EE6123` (Orange)
- Text: `#1A1A1A` (Near black)

**Dark Theme:**
- Background: `#031F39` (Deep blue)
- Surface: `#0A2F4F` (Lighter blue)
- Primary: `#EE6123` (Orange)
- Text: `#E8E8E8` (Light gray)

### Typography
- Font Family: Inter (Google Fonts)
- Base Size: 16px
- Scale: 1.25 (Major Third)

### Components
- Buttons with hover states
- Cards with shadows
- Inputs with focus states
- Toast notifications
- Modal dialogs
- Loading spinners

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=app tests/
```

Run specific test file:

```bash
pytest tests/test_routes.py -v
```

### Test Coverage

The test suite includes:
- ✅ Authentication flow tests
- ✅ Link CRUD operation tests
- ✅ Redirect functionality tests
- ✅ Utility function tests
- ✅ Database model tests

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./gosha.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Account
ADMIN_EMAIL=admin@gosha.link
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin123!

# Application
APP_NAME=Gosha Connections Platform
APP_VERSION=2.0.0
BASE_URL=http://localhost:8000
```

### Configuration File

Edit `app/config.py` to customize:
- Database settings
- JWT configuration
- Admin credentials
- CORS settings
- Upload limits

## 🚀 Deployment

### Production Checklist

- [ ] Change admin password
- [ ] Set strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set `secure=True` for cookies
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Configure CDN for static files

### Docker Deployment (Coming Soon)

```bash
docker build -t url-shortener .
docker run -p 8000:8000 url-shortener
```

## 📈 Performance

- **Fast Response Times** — Optimized database queries with indexes
- **Efficient Redirects** — Direct database lookup for short codes
- **Caching Ready** — Structure supports Redis caching
- **Async Support** — FastAPI async capabilities for high concurrency

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Made with ❤️ by [ternopolskiy](https://github.com/ternopolskiy)**

## 🙏 Acknowledgments

- Inspired by [Bitly](https://bitly.com/)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components inspired by modern design systems
- Icons from emoji set

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact: georg137ternopol@gmail.com

---

**⭐ If you like this project, please give it a star on GitHub!**
