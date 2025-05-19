from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test short summary
def test_summarize_short():
    data = {
        "content": "FastAPI is a fast and efficient web framework.",
        "option": "short",
        "style": "general"
    }
    response = client.post("/summarize", json=data)
    assert response.status_code == 200
    assert "summary_text" in response.json()

# Test medium summary
def test_summarize_medium():
    data = {
        "content": "FastAPI is a modern, fast web framework written in Python, supporting asynchronous operations and boasting excellent performance.",
        "option": "medium",
        "style": "general"
    }
    response = client.post("/summarize", json=data)
    assert response.status_code == 200
    assert "summary_text" in response.json()

# Test long summary
def test_summarize_long():
    data = {
        "content": "FastAPI is a fast, modern framework for web development. It is written in Python and supports asynchronous processing, providing excellent performance. It also offers Swagger UI and ReDoc for API documentation, and automatic API generation based on Python type hints.",
        "option": "long",
        "style": "general"
    }
    response = client.post("/summarize", json=data)
    assert response.status_code == 200
    assert "summary_text" in response.json()
