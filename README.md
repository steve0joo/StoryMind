# StoryMind

**AI-Powered Character Visualization from Literary Works**

StoryMind generates consistent, text-accurate visual representations of characters from books using RAG (Retrieval-Augmented Generation) and Imagen 3 for high-fidelity image generation.

## Project Overview

- **Status:** Pre-development (Hackathon MVP)
- **Target:** 36-hour hackathon for Google Media Mastery track
- **Core Innovation:** Deterministic seed-based character consistency
- **Tech Stack:** Flask + React + LangChain + FAISS + Imagen 3 + Gemini 2.0

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18.0+
- Google AI API Key ([Get one here](https://ai.google.dev/))

### 1. Clone Repository

```bash
git clone <repo-url> storymind
cd storymind
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Initialize database
python init_db.py

# Validate setup
python test_setup.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Run the Application

**Terminal 1 - Backend:**

```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

- Backend API: http://localhost:5000
- Frontend UI: http://localhost:5173

## Project Structure

```
storymind/
├── backend/
│   ├── services/          # Business logic (RAG, character extraction, image gen)
│   ├── models/            # Database models
│   ├── utils/             # Helper functions and caching
│   ├── scripts/           # Demo prep and migration scripts
│   ├── tests/             # Test files
│   ├── static/uploads/    # Local file storage (books & images)
│   ├── app.py             # Flask application
│   ├── init_db.py         # Database initialization
│   ├── test_setup.py      # Environment validation
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── api/           # API client
│   │   └── App.jsx        # Main app component
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── data/
│   ├── uploads/           # Book uploads (alternative location)
│   └── faiss_indices/     # FAISS vector indices
├── docs/                  # Comprehensive documentation

```

## Architecture

```
Frontend (React + Vite)
    ↓ HTTP/REST
Backend (Flask)
    ├── Document Processing (LangChain)
    ├── RAG System (Custom FAISS)
    ├── Character Extraction (Gemini 2.0)
    └── Image Generation (Imagen 3)
    ↓
Data Layer
    ├── SQLite (metadata)
    ├── Local File Storage (uploads & images)
    └── In-memory cache (Python dict)
```

## Key Features

### Core Innovation: Character Consistency

StoryMind uses deterministic seed generation to ensure the same character always looks the same:

```python
import hashlib

def generate_seed(character_name):
    """Same character = same seed = consistent images"""
    name_hash = hashlib.md5(character_name.encode()).hexdigest()
    seed = int(name_hash, 16) % (2**32)
    return seed
```

### Technology Choices

**Backend:**

- **Flask 3.0.3** - Lightweight API server
- **LangChain 0.3.7** - Document loading & text splitting only
- **Direct FAISS 1.9.0** - Custom RAG implementation for full control
- **Gemini 2.0 Flash** - Character extraction & description synthesis
- **Imagen 3** - High-fidelity image generation with seed control

**Frontend:**

- **Vite 5.4.10** - 10x faster than Create React App
- **React 18.3.1** - UI framework
- **Tailwind CSS 3.4.14** - Styling
- **React Force Graph 1.44.7** - Character relationship visualization

## 👥 Team Collaboration (3-Person Team)

### Git Workflow

```bash
main              # Production-ready
  └── develop     # Integration branch
        ├── feature/backend-api    # Person 1: Backend Lead
        ├── feature/ml-pipeline    # Person 2: ML/AI Lead
        └── feature/frontend-ui    # Person 3: Frontend Lead
```

### Roles

- **Person 1: Backend Lead** - Flask API, Database, RAG system
- **Person 2: ML/AI Lead** - Gemini integration, Imagen 3, Character profiles
- **Person 3: Frontend Lead** - React UI, API integration, Styling

## Documentation

- **[docs/StoryMind_PRD.md](docs/StoryMind_PRD.md)** - Product requirements
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[docs/DEPENDENCY_UPDATES.md](docs/DEPENDENCY_UPDATES.md)** - Latest dependency info

## Testing

### Validate Environment Setup

```bash
cd backend
python test_setup.py
```

Expected output:

```
✅ All packages installed correctly
✅ Required environment variables set
✅ Gemini API connected
✅ FAISS working
✅ SQLite working


All systems go!
```

## Demo Preparation

**IMPORTANT:** Pre-generate all demo content before presentation:

```bash
cd backend
source venv/bin/activate
python scripts/demo_prep.py
```

This prevents API rate limits and network issues during live demo.

## Development Commands

### Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask server
python app.py

# Reset database
python init_db.py --reset

# Run tests
pytest
```

### Frontend

```bash
# Start dev server (instant hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Configuration

### Environment Variables

Create `backend/.env` with:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (have defaults)
FLASK_SECRET_KEY=your_random_secret_key
FLASK_DEBUG=True
DATABASE_URL=sqlite:///storymind.db
ALLOWED_ORIGINS=http://localhost:5173
```

## Technology Stack Details

### Why This Stack?

- **Hybrid LangChain Approach:** Use only for document loading & text splitting (~2 hours saved)
- **Custom FAISS:** Full control over RAG
- **Direct Imagen API:** Need deterministic seed control (competitive advantage)
- **SQLite for Hackathon:** Zero setup time, easy migration to PostgreSQL later
- **Local File Storage:** No cloud setup needed, simple Flask static serving

### Version Philosophy

- Latest stable versions (as of November 8, 2025)
- No future-dated versions (Vite 6.x, Tailwind 4.x don't exist yet)
- Security patches applied (Flask 3.0.3, numpy 2.1.3)
- Proven compatibility (React Force Graph 1.44.7)

## Success Metrics (Hackathon)

- ✅ Generate visually consistent characters from 3+ books
- ✅ <5% visual variation for same character across multiple generations
- ✅ End-to-end flow: upload → process → visualize in <60 seconds
- ✅ Top 3 placement in Google Media Mastery track

## Roadmap

### Hackathon (36 hours)

- [x] Documentation complete
- [x] Project structure setup
- [ ] Backend RAG pipeline
- [ ] Character extraction & synthesis
- [ ] Image generation with consistency
- [ ] Frontend UI & API integration
- [ ] Demo preparation

### Post-Hackathon

- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Google Cloud Storage for files
- [ ] User authentication
- [ ] Publisher API
- [ ] Mobile app

## Contributing

This is a hackathon project. For the team:

1. See MD files for your role and tasks
2. Follow Git workflow (feature branches → develop → main)
3. Run `python test_setup.py` before starting
4. Pre-generate demo content with `scripts/demo_prep.py`

## License

This project is licensed under CC BY-NC 4.0. No commercial use allowed without explicit permission.

## Acknowledgments

- Built for Google Media Mastery hackathon
- Uses Gemini 2.0 Flash and Imagen 3

---

**Ready to bring characters to life with AI!**
