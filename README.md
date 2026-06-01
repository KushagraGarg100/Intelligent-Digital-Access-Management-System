# Intelligent Digital Access Management System (IDAMS)

> An AI-powered Digital Asset Management platform for secure storage, intelligent search, version control, and role-based access management of digital resources.

## 📌 Overview

The **Intelligent Digital Access Management System (IDAMS)** is a modern full-stack platform designed to manage, organize, secure, and retrieve digital assets efficiently. The system combines traditional asset management features with **Artificial Intelligence-based semantic search**, enabling users to locate files using natural language queries instead of relying solely on filenames or metadata.

The platform supports secure authentication, role-based access control, version tracking, AI-generated embeddings, and intelligent content indexing, making it suitable for organizations managing large collections of digital assets.

---

## 🚀 Key Features

### 🔐 Secure Authentication & Authorization

* JWT-based authentication
* Role-Based Access Control (RBAC)
* Protected API routes
* Secure user registration and login
* Session management

### 📁 Digital Asset Management

* Upload and manage files
* Asset categorization
* Metadata extraction
* Asset versioning
* File download and retrieval

### 🤖 AI-Powered Semantic Search

* Natural language search
* CLIP-based embedding generation
* Vector similarity matching
* Context-aware asset retrieval
* Intelligent content indexing

### 🏷️ Metadata Management

* Tag-based organization
* Automatic metadata storage
* Advanced filtering capabilities
* Search by filename, tags, or content

### 📚 Version Control

* Asset version history
* Version tracking
* Previous version retrieval
* Change management

### ☁️ Cloud Storage Support

* Google Cloud Storage integration
* Local storage fallback
* Scalable asset storage architecture

---

## 🏗️ System Architecture

```text
┌──────────────────────────┐
│        Frontend          │
│ React + Tailwind CSS     │
└──────────┬───────────────┘
           │ REST API
           ▼
┌──────────────────────────┐
│         Backend          │
│ Flask REST API           │
└──────────┬───────────────┘
           │
 ┌─────────┼─────────┐
 ▼         ▼         ▼
PostgreSQL FAISS   Storage
Metadata  Vector   Layer
Database  Index
           │
           ▼
   AI Processing Layer
(PyTorch + CLIP Model)
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* Tailwind CSS
* Axios
* React Hooks

### Backend

* Flask
* Flask REST API
* Flask-JWT-Extended
* Flask-CORS
* SQLAlchemy

### Database

* PostgreSQL

### AI & Machine Learning

* PyTorch
* Hugging Face Transformers
* CLIP Model
* FAISS Vector Database

### Storage

* Google Cloud Storage
* Local File System Storage

### Security

* JWT Authentication
* Password Hashing
* RBAC Authorization
* SHA-256 Content Hashing

---

## 📂 Project Structure

```bash
Intelligent-Digital-Access-Management-System/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── services/
│
├── backend/
│   ├── app/
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── utils/
│
├── ai_service/
│   ├── embedding/
│   ├── indexing/
│   └── search/
│
├── storage/
│
├── database/
│
├── uploads/
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Core Functionalities

### User Management

* User Registration
* User Login
* JWT Token Generation
* Role Management

### Asset Upload

* Upload digital assets
* Store metadata
* Generate content hash
* Trigger AI processing pipeline

### Semantic Search

* Generate embeddings using CLIP
* Store vectors in FAISS
* Perform similarity matching
* Return relevant assets

### Asset Versioning

* Create new asset versions
* Maintain version history
* Retrieve previous versions

### Download Management

* Secure file retrieval
* Access control validation
* Download tracking

---

## 🔄 Workflow

### Upload Workflow

```text
User Uploads Asset
        │
        ▼
Metadata Extraction
        │
        ▼
SHA-256 Hash Generation
        │
        ▼
Asset Stored in Storage
        │
        ▼
AI Embedding Generation
        │
        ▼
FAISS Index Update
        │
        ▼
Search Ready
```

### Search Workflow

```text
User Search Query
        │
        ▼
Text Embedding Generation
        │
        ▼
FAISS Similarity Search
        │
        ▼
Relevant Assets Retrieved
        │
        ▼
Results Displayed
```

---

## 🔑 API Endpoints

### Authentication

```http
POST /register
POST /login
```

### Asset Management

```http
POST   /upload
GET    /assets
GET    /assets/<id>
DELETE /assets/<id>
```

### Version Control

```http
POST /assets/<id>/version
GET  /assets/<id>/history
```

### Search

```http
POST /search
```

---

## 📊 Database Design

### Users Table

| Field         | Type    |
| ------------- | ------- |
| id            | Integer |
| username      | String  |
| email         | String  |
| password_hash | String  |
| role          | String  |

### Assets Table

| Field        | Type      |
| ------------ | --------- |
| id           | Integer   |
| filename     | String    |
| storage_path | String    |
| hash         | String    |
| uploaded_by  | Integer   |
| created_at   | Timestamp |

### Versions Table

| Field          | Type      |
| -------------- | --------- |
| id             | Integer   |
| asset_id       | Integer   |
| version_number | Integer   |
| created_at     | Timestamp |

---

## 🔍 AI Search Pipeline

1. User submits a search query.
2. Query is converted into embeddings using the CLIP model.
3. Embeddings are compared against stored vectors in FAISS.
4. Similar assets are identified using vector similarity.
5. Ranked results are returned to the user.

---

## 📈 Performance Optimizations

* Vector-based semantic retrieval using FAISS
* Indexed PostgreSQL queries
* Metadata caching
* Efficient asset retrieval
* Modular service architecture
* Optimized API response handling

---

## 🔒 Security Features

* JWT Authentication
* Password Hashing
* Role-Based Access Control
* Secure File Access
* SHA-256 Integrity Verification
* Input Validation
* Protected API Endpoints

---

## 🌟 Future Enhancements

* Multi-factor authentication (MFA)
* AI-powered asset tagging
* OCR for document understanding
* Real-time collaboration
* Advanced analytics dashboard
* Microservices deployment architecture
* Kubernetes-based scaling
* Multi-cloud storage support

---

## 👨‍💻 Contributors

### Architecture & Development

* Kushagra Garg

---

## 📄 License

This project is developed for educational and research purposes. Modify and extend according to your organizational requirements.


Built with AI, Cloud Technologies, Vector Search, and Secure Access Management to simplify digital asset organization and retrieval.
