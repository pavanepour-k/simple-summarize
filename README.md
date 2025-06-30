# 📄 SimpleSummarize

**SimpleSummarize** is a modular, FastAPI-based text summarization API.  
This project is being rebuilt from scratch to ensure better maintainability, modularity, and modern development practices.

> ⚠️ **Note**: This is a clean reinitialization of the original `SimpleSummarize` project. Features are being reimplemented step-by-step.

---

## 🚧 In Progress

- ✅ Clean project scaffolding with FastAPI
- ⏳ Core API: basic text summarization
- ⏳ File upload support (PDF/DOCX)
- ⏳ Multilingual support
- ⏳ Authentication (JWT/API Key)
- ⏳ Admin/statistics API
- ⏳ Rate limiting middleware
- ⏳ Deployment, CI, testing setup

---

## ✨ Planned Features

- **Text Summarization**: Extractive & abstractive methods
- **Style Options**: `general`, `problem_solver`, `emotion_focused`
- **File Upload**: Summarize content from PDF and DOCX files
- **Multilingual**: English, Korean, Japanese (more to come)
- **Secure API**: JWT-based and API key access
- **Admin Panel**: Usage stats, rate limits, logs
- **Debug Mode**: Developer-visible prompt/logging options

---

## ⚙️ Getting Started

### 1. Clone and set up the project

```bash
git clone https://github.com/your-username/simple-summarize.git
cd simple-summarize

```
<br>

### 2. Create and activate a virtual environment
<br>

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
<br>

### 3. Install dependencies
<br>

```
pip install -r requirements.txt
```
<br>

### 4. Create a .env file

<br>
Start with:

```
API_KEY=your-api-key
DEBUG_MODE=True
API_ROLE=user
```
<br>

### 5. Run the server

<br>
```
uvicorn app.main:app --reload
```
<br>

Visit: http://127.0.0.1:8000/docs

## 📦 Tech Stack

| Purpose           | Stack                                          |
| ----------------- | ---------------------------------------------- |
| **Language**      | Python 3.10                                   |
| **Framework**     | FastAPI + Uvicorn                              |
| **Validation**    | Pydantic v2, python-dotenv                     |
| **Security**      | JWT (python-jose), Cryptography                |
| **File Handling** | PyMuPDF, python-docx (planned)                 |
| **Utils**         | Custom logging, config, and exception handlers |




## 📁 Documentation

<br>

| Doc                                             | Description                               |
| ----------------------------------------------- | ----------------------------------------- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)    | Project architecture and module structure |
| [docs/API\_REFERENCE.md](docs/API_REFERENCE.md) | REST API endpoints (in progress)          |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)        | Deployment guide and environment setup    |

<br>

> You can also browse the API via /docs when the server is running.


## 🛡️ Security Practices

<br>

  - Never commit .env or sensitive credentials

  - Use environment variables or secret managers in production

  - JWT and API key authentication will be applied

<br>
---

## 🧾 Project Info

### License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for full terms.

<br>

---

### Contributing

Contributions are welcome!
Please fork the repo, open issues, or submit pull requests under the MIT License.
<br> <br>
