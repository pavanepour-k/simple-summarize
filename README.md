# 📄 SimpleSummarize

**SimpleSummarize** is a FastAPI-based web API for quick and flexible text summarization. It supports both extractive and abstractive summaries, multiple summarization styles, and file uploads (PDF, DOCX). Designed with performance and modularity in mind.
<br><br>

---

## ✨ Key Features

-  **Text Summarization**: Extractive & abstractive methods
-  **Style Options**: `general`, `problem_solver`, `emotion_focused`
-  **File Upload Support**: Summarize from PDF or DOCX
-  **Multilingual**: English, Korean, Japanese (more planned)
-  **Secure API Access**: JWT & API Key authentication
-  **Admin API**: Usage stats and logs for administrators
-  **Rate Limiting**: Role-based usage control
-  **Debug Mode Support**: Optional visibility of prompt data
<br><br>

---

## Getting Started

### 1. Clone the Repository
<br>

```bash
git clone https://github.com/your-username/simple-summarize.git
cd simple-summarize
```
<br>

### 2. Set Up Environment
<br>

```
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
<br>

### 3. Configure .env
<br>
Create a .env file with:
<br>

```
API_KEY=your-api-key
DEBUG_MODE=True
API_ROLE=user
MAX_FILE_SIZE=50MB
```
<br>

### 4. Run the Server
<br>

```
uvicorn main:app --reload
```
<br>
Visit: http://127.0.0.1:8000
<br><br>

## Usage Examples

### Text Summarization
```
POST /summarize/text
Content-Type: application/json

{
  "content": "Your long text here...",
  "style": "general"
}
```


### File Upload
```
POST /summarize/file?style=general
Content-Type: multipart/form-data

file=<your_file.pdf or .docx>
```
---



## Security Best Practices


- Store credentials (e.g., API_KEY, SECRET_KEY) in .env and do not commit this file.

- For production, consider using secret managers (e.g., AWS Secrets Manager, Azure Key Vault).

- JWT tokens are used for user authentication and access control.

---



## ⚙️ Technology Stack

| Category          | Stack                                      |
| ----------------- | ------------------------------------------ |
| **Language**      | Python 3.11                                |
| **Framework**     | FastAPI, Uvicorn (ASGI server)             |
| **Validation**    | Pydantic, Pydantic Settings, python-dotenv |
| **Security**      | JWT via python-jose, Cryptography          |
| **File Handling** | PyMuPDF, python-docx                       |
| **Caching**       | Redis (via async connection pool)          |
| **Utilities**     | requests, custom error/logging utils       |


---


## 🧾 Project Info

### License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for full terms.

<br>

---

### Contributing

Feel free to fork the repo, open issues, or submit pull requests.  
All contributions are made under the MIT License.
<br> <br>

---

### Docs

The following documents are currently under preparation.  
Links are placeholders and will be updated soon:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Internal file/module structure *(Coming soon)*
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md): Environment & production setup guide *(Coming soon)*
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md): Full API reference *(Coming soon — you can still access `/docs` in the meantime)*
