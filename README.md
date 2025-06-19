# Overview

**SimpleSummarize** quickly and accurately summarizes long texts. Based on the user's input, it provides both extractive and abstractive summaries and supports various summarization styles. Built with FastAPI and Uvicorn, it follows a RESTful design.

---

## Key Features

- **Text Summarization**: Summarizes the provided text using extractive and abstractive methods.
  
- **Summary Styles**: Supports `general`, `problem_solver`, and `emotion_focused` styles.
  
- **File Upload**: Supports uploading PDFs and DOCX files, extracting text, and summarizing.
  
- **Multilingual Support**: Summarizes text in multiple languages, including English, Japanese, and Korean. Support for additional languages is planned for future updates.
  
- **API Rate Limiting**: Built-in API rate limiting based on subscription plans and user roles.
  
- **Debugging Mode**: The `style_prompt` field is only returned in debugging mode, ensuring sensitive information is not exposed in production.


---

## API Features (summarize_router.py)

- Basic text summarization and file upload summarization features are implemented.

- API key authentication and user authentication are properly handled.

- The style_prompt field is configured to only be returned in debugging mode, ensuring that sensitive information is not exposed in production environments.

## Admin API (admin_router.py)

- An admin-exclusive statistics and log viewing API has been implemented, allowing administrators to check system usage and recent logs.

- Admin authentication is handled by the verify_admin function to verify admin privileges.

## Plan and Rate Limit Management (plan_config.py)

- API call limits and time-based restrictions according to the plan are properly implemented.

- A dynamic processing approach is used, taking into account plan-specific and time-based restrictions.

## Environment Variable Management (settings.py, config_manager.py)

- Important environment variables (such as API_KEY, SECRET_KEY) are loaded from the .env file and securely handled using pydantic-settings.

- Redis and connection pool management are optimized, and environment variables are configured flexibly.

## File Validation and Processing (file_parser.py)

- File size and format validation have been enhanced, ensuring thorough validation of uploaded files.

- Logic for handling PDF and DOCX files is well-implemented, and text extraction and file validation processes are efficiently managed.

## Redis Client and Performance Optimization (redis_client.py)

- Performance optimization is achieved using Redis connection pools and asynchronous clients.

- Backpressure and timeout management are appropriately handled, and retry logic is in place to enhance stability.

## JWT Authentication and Security (jwt_handler.py)

- API access is protected using JWT authentication along with API key and user authentication.

- Token generation and validation logic are well-implemented.

## Utilities and Error Handling (error_handler.py)

- Exception handling is finely detailed, with appropriate HTTP status codes and logging for any errors that occur.

- HTTPException handling is granular, allowing clear processing of errors.

## Analytics and Log Processing (analytics.py)

- API usage statistics and log recording are effectively handled, with batch processing and log storage integrated with Redis for efficient operation.

## Main Application (main.py)

- The FastAPI application is configured, with CORS middleware and file size limit middleware properly applied.

- Logging during server startup and shutdown is set up, and a health check endpoint (GET /) is well-configured.

---

## Technology Stack

### Programming Language

- **Python 3.11**: The project is built using Python 3.11, ensuring compatibility with the latest Python features and performance improvements.

### Backend Framework

- **FastAPI (v0.110.1)**: A modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Uvicorn (v0.29.0)**: An ASGI server for serving FastAPI applications, known for its speed and performance.

### Data Validation & Configuration

- **Pydantic (v2.11.4)**: Data validation and settings management library for Python, used for parsing and validating input data.
- **Pydantic Settings (v2.2.1)**: A Pydantic extension used for managing environment variables and configuration settings with type safety.
- **python-dotenv (v1.0.1)**: Loads environment variables from a `.env` file for easy configuration management.

### Authentication & Security

- **python-jose (v3.3.0)**: A library for handling JWT (JSON Web Tokens) to secure API access with user authentication.
- **cryptography (v38.0.1)**: A library used for encryption, key management, and secure token handling.

### File Handling & Parsing

- **PyMuPDF (v1.23.22)**: A library for handling PDF files, used for text extraction and file manipulation.
- **python-docx (v1.1.0)**: A library for parsing and handling DOCX files, including extracting text content.
- **fitz (v1.0.0)**: Another library related to PyMuPDF, used for working with PDF files (text extraction, manipulation).

### Caching & Data Storage

 - **Redis (v6.0.0)**: A high-performance in-memory data store used for caching and managing connection pools.

### HTTP Requests & External Communication

 - **requests (v2.32.3)**: A simple HTTP library for making requests to external services or APIs.

### Environment Configuration & Dependency Management


### Rate Limiting & Request Handling

- Custom rate-limiting logic implemented based on user roles and subscription plans.

### Logging & Monitoring

- Custom logging configuration to track server activity, errors, and usage patterns.


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

---

## Open Source Libraries and Licenses Used

This project utilizes several open-source libraries that are licensed under various open-source licenses. Below is a list of the libraries used and their respective licenses:

- **FastAPI**: MIT License  
  FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

- **Uvicorn**: MIT License  
  Uvicorn is a lightning-fast ASGI server implementation, using uvloop and httptools.

- **Pydantic**: MIT License  
  Pydantic is used for data validation and settings management. It enforces type annotations at runtime.

- **Pydantic-settings**: MIT License  
  Pydantic Settings is used to load settings in a structured manner, managing application configurations from environment variables.

- **python-dotenv**: MIT License  
  python-dotenv reads key-value pairs from a .env file and sets them as environment variables.

- **Redis**: MIT License  
  Redis is an in-memory data structure store, often used as a database, cache, and message broker.

- **PyMuPDF**: Mozilla Public License 2.0 (MPL-2.0)  
  PyMuPDF is a Python binding for MuPDF, a lightweight PDF, XPS, and eBook viewer.

- **python-docx**: MIT License  
  python-docx is used for creating, modifying, and extracting information from Word documents (.docx).

- **python-jose**: MIT License  
  Python-JOSE is a library for creating and verifying JSON Web Tokens (JWT).

- **Cryptography**: MIT License  
  The cryptography package is used to provide cryptographic recipes and primitives to Python developers.

- **Requests**: Apache License 2.0  
  Requests is a simple HTTP library for Python, designed to be user-friendly and to handle HTTP requests easily.

- **PyTorch**: BSD-3-Clause License  
  PyTorch is an open-source machine learning library used for computer vision and natural language processing.

- **TensorFlow**: Apache License 2.0  
  TensorFlow is an open-source machine learning framework developed by Google, used for a wide range of AI tasks.

- **Flax**: Apache License 2.0  
  Flax is a high-performance neural network library for JAX, designed to make machine learning research easy to implement.

### License Compliance
This project complies with the licenses of the libraries used, and the full text of the licenses for each of these libraries can be found in the respective library repositories or on their respective PyPI pages.



---


### Deployment Considerations

Licenses: All open source libraries used in this project follow either the MIT License or BSD-3-Clause License. You should include the appropriate licenses in your distribution and comply with their terms.

Environment Variables Security: Ensure API_KEY and sensitive information are securely managed. Do not hardcode sensitive information in the code, and make use of environment variables for secure handling.



### Contributing

If you'd like to contribute, please fork this repository and submit a pull request.
All contributions are made under the MIT License.




This README file provides information about the SimpleSummarize project, including its setup, installation, usage, and licensing.
It also covers the importance of security when handling environment variables and how to ensure compliance with open-source licenses.



---

This **README** file is designed to help developers quickly understand how to set up and use the API while also providing security best practices and licensing information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.