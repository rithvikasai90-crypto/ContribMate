
# 🚀 ContribMate

Your AI companion for open-source contributions.

ContribMate is an AI-powered web application that helps beginners explore GitHub repositories, discover beginner-friendly issues, and understand how to contribute to open-source projects.

## ✨ Features

- GitHub Repository Explorer
- AI-powered Contribution Guide
- Beginner-Friendly GitHub Issues
- AI Issue Explanation
- Issue Difficulty and Skills Analysis
- Markdown-formatted AI responses

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- GitHub REST API

### Artificial Intelligence
- Ollama
- Gemma 4 (`gemma4:e2b`)

## 📁 Project Structure

```text
ContribMate/
├── backend/
│   ├── main.py
│   ├── github_service.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python 3.12
- Node.js and npm
- Ollama
- Git

### 1. Clone the Repository

After this project is published to GitHub, clone it using its repository URL.

### 2. Download the AI Model

```bash
ollama pull gemma4:e2b
```

Make sure Ollama is running.

### 3. Start the Backend

Open a terminal in the `backend` folder.

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend URL: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

### 4. Start the Frontend

Open another terminal in the `frontend` folder.

```bash
npm install
npm run dev
```

On Windows PowerShell, use `npm.cmd` instead of `npm` if needed.

The frontend displays the backend address and proxies API requests to
`http://127.0.0.1:8000` by default. To use a different backend, create
`frontend/.env` with:

```env
VITE_BACKEND_URL=http://127.0.0.1:8000
```

Restart the frontend after changing this value. The backend address links to
its API documentation at `/docs`.

Frontend URL: http://localhost:5173/

## 🚀 How to Use

1. Open ContribMate in your browser.
2. Paste a GitHub repository URL.
3. Click "Analyze Repository".
4. Read the AI-generated contribution guide.
5. Explore issues labeled "good first issue".
6. Click "Explain This Issue" to get a beginner-friendly explanation.

## 🔮 Future Improvements

- Personalized issue recommendations
- AI-based issue difficulty ranking
- Contribution progress tracking
- README and contribution guideline analysis
- Automated testing

## ⚠️ Important Notes

- AI-generated explanations may contain mistakes.
- GitHub API rate limits may apply.
- The local AI model must be installed and running.
- A "good first issue" label does not guarantee that an issue is easy.

## 📄 License

A license has not yet been selected.

---

Made to help beginners start contributing to open source.
