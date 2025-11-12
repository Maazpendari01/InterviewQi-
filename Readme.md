# AI Interview Platform - Backend

AI-powered technical interview platform with RAG-based evaluation using Groq LLaMA and LangGraph.

## 🚀 Features

- **Multi-Category Interviews**: Coding, System Design, Behavioral questions
- **RAG Evaluation**: Compares answers against expert responses using vector similarity
- **Smart Follow-ups**: Generates contextual follow-up questions based on performance
- **Progress Tracking**: Saves all sessions with detailed analytics
- **JWT Authentication**: Secure user authentication and session management

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM + SQLite database)
- LangChain + LangGraph (AI orchestration)
- Groq API (LLaMA 3.1/3.3 models)
- ChromaDB (Vector database)
- HuggingFace Transformers (Embeddings)

**AI/ML:**
- Sentence Transformers (all-MiniLM-L6-v2)
- RAG (Retrieval-Augmented Generation)
- Multi-agent interview flow with LangGraph

## 📋 Prerequisites

- Python 3.10+
- Groq API Key ([Get it here](https://console.groq.com))
- Git

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd tech-interview-ai
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Set Up Environment Variables
Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_for_jwt
DATABASE_URL=sqlite:///./backend/data/app.db
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Initialize Database
```bash
python -m backend.app.models.database
```

This creates:
- SQLite database at `backend/data/app.db`
- Tables: users, interview_sessions, question_responses, weak_areas

### 6. Load Interview Questions (RAG Setup)
```bash
python -m backend.app.services.knowledge_base
```

This will:
- Load 50+ questions from `backend/data/interview_qa.json`
- Generate embeddings using sentence-transformers
- Store vectors in ChromaDB at `backend/data/chroma_db/`
- Takes 30-60 seconds on first run

### 7. Start Server
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

Swagger docs: `http://localhost:8000/docs`

## 🧪 Test the API

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123"
```

### Start Interview (use token from login)
```bash
curl -X POST "http://localhost:8000/api/interview/start" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"category": "coding", "difficulty": "medium"}'
```

## 📁 Project Structure
```
backend/
├── app/
│   ├── models/
│   │   └── database.py          # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── interview.py         # Interview endpoints
│   │   └── analytics.py         # Analytics endpoints
│   ├── services/
│   │   ├── interview_graph.py   # LangGraph interview flow
│   │   ├── knowledge_base.py    # RAG vector store
│   │   └── db_service.py        # Database operations
│   ├── auth/
│   │   ├── security.py          # Password hashing, JWT
│   │   └── dependencies.py      # Auth dependencies
│   └── main.py                  # FastAPI app
├── data/
│   ├── interview_qa.json        # 50+ interview questions
│   ├── chroma_db/               # Vector database (gitignored)
│   ├── models/                  # Downloaded embeddings (gitignored)
│   └── app.db                   # SQLite database (gitignored)
└── requirements.txt
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)
- `GET /api/auth/me` - Get current user info

### Interview
- `POST /api/interview/start` - Start new interview session
- `POST /api/interview/answer` - Submit answer to current question
- `GET /api/interview/{session_id}/summary` - Get interview results
- `GET /api/interview/sessions/recent` - Get recent sessions

### Analytics
- `GET /api/analytics/overview` - Platform statistics
- `GET /api/analytics/weak-areas` - Identify weak topics

## 🧠 How RAG Evaluation Works

1. **Question Retrieval**: User gets a question from the knowledge base
2. **Answer Submission**: User submits their answer
3. **Vector Search**: System finds similar expert answers using embeddings
4. **LLM Evaluation**: Groq LLaMA compares user answer vs expert examples
5. **Scoring**: Returns score (0-100) + detailed feedback
6. **Follow-up Generation**: Creates contextual follow-up question

## 🚀 Deployment

### Option 1: Render
1. Create new Web Service on Render
2. Connect your GitHub repo
3. Build command: `pip install -r backend/requirements.txt`
4. Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `GROQ_API_KEY`, `SECRET_KEY`

### Option 2: Railway
1. Create new project on Railway
2. Connect GitHub repo
3. Add environment variables
4. Deploy

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |
| `SECRET_KEY` | JWT secret key (generate with `secrets.token_urlsafe(32)`) | Yes |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

## 🐛 Troubleshooting

### ChromaDB Issues
```bash
# Delete and rebuild vector database
rm -rf backend/data/chroma_db/
python -m backend.app.services.knowledge_base
```

### Database Issues
```bash
# Reset database
rm backend/data/app.db
python -m backend.app.models.database
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

## 📝 License

MIT

## 🔗 Frontend

Frontend repo: [interviewiq-sparkle](https://github.com/Maazpendari01/interviewiq-sparkle)

## 👤 Author

Your Name - [GitHub](https://github.com/Maazpendari01)
