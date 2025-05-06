# SimpleSummarize API

**SimpleSummarize API** is an API that quickly and accurately summarizes long texts. It supports various text summarization styles and provides both extractive and abstractive summaries based on the user's input. The API is built using FastAPI and Uvicorn and follows a RESTful design.

---

## Key Features

- **Text Summarization**: Summarizes the provided text using extractive and abstractive methods.
- **Summary Styles**: Supports `general`, `problem_solver`, `emotion_focused` styles.
- **File Upload**: Supports uploading PDFs and DOCX files, extracting text, and summarizing.
- **Multilingual Support**: Summarizes text in multiple languages, including English, Korean, and Japanese.
- **API Rate Limiting**: Built-in API rate limiting based on subscription plans and roles.
- **Debugging Mode**: The `style_prompt` field is only returned in debugging mode.

---

## Technology Stack

- **FastAPI** - High-performance web framework
- **Uvicorn** - Asynchronous web server
- **Pydantic** - Data modeling and validation
- **Redis** - API rate limiting and caching
- **Celery** - Asynchronous task processing
- **python-dotenv** - Environment variable management

---

### Explanation of Sections:

1. **Installation**: Includes the steps to clone the repository, set up the environment, install dependencies, and run the API server.
2. **Usage**: Provides examples of how to make requests to the API for text and file summarization.
3. **Security**: Stresses the importance of securely managing environment variables (especially API keys).
4. **License**: Specifies the project license (MIT) and lists the licenses for the open-source libraries used in the project.
5. **Deployment Considerations**: Ensures that developers handle sensitive data correctly and comply with the licenses of any third-party libraries used.


---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/simple-summarize.git
cd simple-summarize
```

### 2. Create a Virtual Environment (Optional)
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Set Up .env File

Create a .env file and set the necessary environment variables. Example:
```
API_KEY=your-api-key-here
DEBUG_MODE=True
API_ROLE=user
MAX_FILE_SIZE=50MB
```
### 5. Run the Server
```
uvicorn main:app --reload
```
The API will be accessible at http://127.0.0.1:8000.

## Usage
Basic Summarization Request
```
POST http://127.0.0.1:8000/summarize/text
Content-Type: application/json
{
  "content": "Your long text here.",
  "style": "general"
}
```
File Upload Summarization Request
```
POST http://127.0.0.1:8000/summarize/file?style=general
Content-Type: multipart/form-data
{
  "file": <your_file.pdf>
}
```

## Security

API_KEY and other sensitive information are managed through the .env file. Ensure that the .env file is gitignored to prevent it from being tracked by version control.

Important: The .env file should not be publicly accessible. Consider using key management systems (e.g., AWS Secrets Manager, Azure Key Vault) to securely manage sensitive data in production environments.



## License

This project is licensed under the MIT License. See the LICENSE file for more details.
### Open Source Libraries and Licenses Used

Celery: BSD-3-Clause License

FastAPI: MIT License

JWT: MIT License

langdetect: Apache License 2.0

Pydantic: MIT License

Pydantic-settings: MIT License

PyMuPDF: GNU Affero General Public License v3.0 (AGPL-3.0)

python-docx: MIT License

python-dotenv: MIT License

Redis-py: MIT License

transformers: Apache License 2.0

Uvicorn: MIT License

Pytest: MIT License





### Deployment Considerations

Licenses: All open source libraries used in this project follow either the MIT License or BSD-3-Clause License. You should include the appropriate licenses in your distribution and comply with their terms.

Environment Variables Security: Ensure API_KEY and sensitive information are securely managed. Do not hardcode sensitive information in the code, and make use of environment variables for secure handling.



### Contributing

If you'd like to contribute, please fork this repository and submit a pull request.
All contributions are made under the MIT License.




This README file provides information about the SimpleSummarize API project, including its setup, installation, usage, and licensing.
It also covers the importance of security when handling environment variables and how to ensure compliance with open-source licenses.


### Contributing

To contribute, fork this repository and submit a pull request. All contributions are made under the MIT License.

---

This **README** file is designed to help developers quickly understand how to set up and use the API while also providing security best practices and licensing information.
