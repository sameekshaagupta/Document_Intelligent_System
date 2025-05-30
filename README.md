# 📚 Document Intelligence Platform

A full-stack **Document Intelligence Platform** with **Retrieval Augmented Generation (RAG)** capabilities, built using **Django REST Framework** and **React**. Upload documents, process them with AI, and ask intelligent questions with contextual answers.

---

## 🚀 Features

* **📄 Document Upload & Processing**: Support for `.txt`, `.pdf`, `.docx` files
* **🔍 RAG Pipeline**: Text chunking, embedding generation, and vector search
* **🧠 Intelligent Q\&A**: Ask questions and receive contextual answers
* **🎨 Modern UI**: Clean, responsive interface styled with Tailwind CSS
* **⚡ Real-time Processing**: Live status and progress indicators
* **📌 Source Citations**: Responses include referenced document chunks
* **💬 Chat History**: Persistent conversation tracking
* **🧮 Vector Database**: ChromaDB integration for similarity search

---

## 🛠️ Tech Stack

### Backend

* Django REST Framework
* ChromaDB
* Sentence Transformers
* OpenAI API / LM Studio
* MySQL
* Python 3.8+

### Frontend

* React 18
* Tailwind CSS
* Axios
* Modern JavaScript (ES6+)

---

## 📋 Prerequisites

Make sure you have the following installed:

* [Python 3.8+](https://www.python.org/downloads/)
* [Node.js 16+](https://nodejs.org/)
* [MySQL 8.0+](https://dev.mysql.com/downloads/)
* [Git](https://git-scm.com/downloads)

---

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd document-intelligence-platform
```

### 2. Backend Setup

#### a. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### b. Install Dependencies

```bash
pip install -r requirements.txt
```

#### c. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=document_intelligence
DB_USER=doc_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

OPENAI_API_KEY=your-openai-api-key
# or for LM Studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model

MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=txt,pdf,docx
```

#### d. Setup MySQL Database

```sql
CREATE DATABASE document_intelligence;
CREATE USER 'doc_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON document_intelligence.* TO 'doc_user'@'localhost';
FLUSH PRIVILEGES;
```

#### e. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### f. (Optional) Create Superuser

```bash
python manage.py createsuperuser
```

#### g. Start Backend Server

```bash
python manage.py runserver
```

Backend will run at `http://localhost:8000`

---

### 3. Frontend Setup

#### a. Navigate to Frontend Directory

```bash
cd ../frontend
```

#### b. Install Dependencies

```bash
npm install
```

#### c. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_UPLOAD_MAX_SIZE=52428800
```

#### d. Start Development Server

```bash
npm start
```

Frontend will run at `http://localhost:3000`

---

## 📁 Project Structure

```
document-intelligence-platform/
├── backend/
│   ├── document_intelligence/
│   ├── documents/
│   ├── media/
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## 💡 Usage Guide

### 1. Upload Documents

* Drag & drop or select `.txt`, `.pdf`, `.docx` files
* View real-time processing status

### 2. Ask Questions

* Go to Q\&A section
* Type your question
* Get AI-generated answers with references

### 3. Manage Documents

* View and delete uploaded documents

---

## 🧪 Testing

### Backend

```bash
cd backend
python manage.py test
```

### Frontend

```bash
cd frontend
npm test
```

---

## 📊 API Endpoints

| Method | Endpoint                 | Description        |
| ------ | ------------------------ | ------------------ |
| GET    | `/api/documents/`        | List all documents |
| POST   | `/api/documents/upload/` | Upload a document  |
| DELETE | `/api/documents/{id}/`   | Delete a document  |
| POST   | `/api/documents/ask/`    | Ask a question     |

---

## 🐛 Troubleshooting

### 1. Database Connection Error

> "Can't connect to MySQL server"

* Ensure MySQL is running and credentials are correct.

### 2. CORS Error

> "Access blocked by CORS policy"

* Add `http://localhost:3000` to `CORS_ALLOWED_ORIGINS` in Django settings.

### 3. OpenAI API Error

> "AuthenticationError"

* Verify your API key is valid and present in `.env`.

### 4. File Too Large

> "Request Entity Too Large"

* Increase upload limits in `settings.py`

---

## 📦 Deployment

### Production Tips

**Backend**:

* Set `DEBUG=False`
* Use Gunicorn + Nginx
* Serve static files via CDN or WhiteNoise

**Frontend**:

* Build production assets: `npm run build`
* Serve via Nginx or similar

### Docker Deployment (Optional)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_HOST=db
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: document_intelligence
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

---

## 🤝 Contributing

1. Fork this repo
2. Create a new branch: `git checkout -b feature/feature-name`
3. Make your changes
4. Commit: `git commit -m "Added feature"`
5. Push: `git push origin feature/feature-name`
6. Submit a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

* OpenAI for LLMs
* ChromaDB for vector search
* Django and React communities

---

**Happy Document Intelligence! 🚀**
