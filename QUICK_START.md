# StoryMind Quick Start Guide

## One-Command Startup

### **Start Everything**

```bash
./start.sh
```

That's it! This will:

- ✅ Start backend on http://localhost:5001
- ✅ Start frontend on http://localhost:5173
- ✅ Check ports and clear conflicts automatically
- ✅ Show live logs from both servers
- ✅ Handle shutdown gracefully with Ctrl+C

---

## Alternative: Development Helper Script

### **See All Commands**

```bash
./dev.sh
```

### **Common Commands**

| Command              | Description                  |
| -------------------- | ---------------------------- |
| `./dev.sh start`     | Start both servers           |
| `./dev.sh stop`      | Stop all servers             |
| `./dev.sh restart`   | Restart everything           |
| `./dev.sh status`    | Check if servers are running |
| `./dev.sh open`      | Open app in browser          |
| `./dev.sh logs`      | View live logs               |
| `./dev.sh db-status` | Check database content       |
| `./dev.sh db-clean`  | Clean database completely    |
| `./dev.sh test-rag`  | Test RAG quality             |
| `./dev.sh test-api`  | Test API endpoints           |

---

## Manual Startup (Old Way)

If you prefer manual control:

### **Backend**

```bash
cd backend
source venv/bin/activate
python app.py
```

### **Frontend** (in new terminal)

```bash
cd frontend
npm run dev
```

---

## First Time Setup

### **Backend Setup** (One time only)

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

### **Frontend Setup** (One time only)

```bash
cd frontend
npm install
```

### **Environment Variables**

Create `backend/.env`:

```bash
GOOGLE_API_KEY=your_google_api_key_here
FLASK_PORT=5001
FLASK_DEBUG=True
```

---

## Usage Examples

### **Scenario 1: Daily Development**

```bash
# Start everything
./start.sh

# Open browser automatically (in another terminal)
./dev.sh open

# When done, press Ctrl+C in start.sh terminal
```

### **Scenario 2: Testing**

```bash
# Start servers
./dev.sh start

# Check status
./dev.sh status

# Test RAG quality
./dev.sh test-rag

# Test API
./dev.sh test-api

# Stop servers
./dev.sh stop
```

### **Scenario 3: Database Cleanup**

```bash
# Check current database
./dev.sh db-status

# Clean everything
./dev.sh db-clean

# Restart with fresh database
./dev.sh restart
```

---

## Troubleshooting

### **Port Already in Use**

```bash
# Stop everything
./stop.sh

# Or manually:
lsof -ti:5001 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### **Backend Won't Start**

```bash
# Check logs
./dev.sh logs-backend

# Or:
tail -f backend/logs/storymind.log
```

### **Frontend Won't Start**

```bash
# Check logs
./dev.sh logs-frontend

# Reinstall dependencies:
cd frontend
rm -rf node_modules
npm install
```

### **Check Everything is Working**

```bash
./dev.sh test-api
```

---

## URLs

| Service            | URL                                         |
| ------------------ | ------------------------------------------- |
| **Frontend**       | http://localhost:5173                       |
| **Backend API**    | http://localhost:5001                       |
| **API Health**     | http://localhost:5001/api/health            |
| **Books API**      | http://localhost:5001/api/books             |
| **Characters API** | http://localhost:5001/api/characters/health |

---

## Log Files

| Log                    | Location                             |
| ---------------------- | ------------------------------------ |
| **Backend**            | `backend.log` (when using start.sh)  |
| **Frontend**           | `frontend.log` (when using start.sh) |
| **Backend (detailed)** | `backend/logs/storymind.log`         |

---

## Demo Preparation

```bash
# 1. Clean database
./dev.sh db-clean

# 2. Start servers
./start.sh

# 3. Open browser (in another terminal)
./dev.sh open

# 4. Upload your demo books via UI

# 5. Check progress
./dev.sh db-status

# 6. Generate images for characters
# (Click "Generate Image" in the UI)
```

---

## Production Build

### **Frontend**

```bash
cd frontend
npm run build
npm run preview  # Test production build
```

### **Backend**

```bash
cd backend
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## Tips

1. **Always use `./start.sh` for development** - It handles everything
2. **Use `./dev.sh status` to check if servers are running**
3. **Press Ctrl+C in the start.sh terminal to stop gracefully**
4. **Use `./dev.sh db-status` to monitor your data**
5. **Check logs with `./dev.sh logs` if something goes wrong**

---

## Next Steps

After servers are running:

1. **Upload a book**: Click "Upload Book" in the UI
2. **Wait for processing**: ~3-4 minutes per book
3. **View characters**: Click "View Details" on the book
4. **Generate images**: Click "Generate Image" for each character
5. **Explore graph**: Click "Graph View" to see character relationships

Enjoy using StoryMind! 🎨📚
