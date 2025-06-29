import pytest
from app.services.models.dummy import DummyModel


class TestDummyModel:
    def test_load(self):
        model = DummyModel()
        model.load("/path/to/model")
        assert model._loaded is True
        assert model._model_path == "/path/to/model"
    
    def test_summarize_not_loaded(self):
        model = DummyModel()
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.summarize("text", 100, 50)
    
    def test_summarize(self):
        model = DummyModel()
        model.load("dummy")
        
        text = "This is a long text that needs to be summarized"
        result = model.summarize(text, 100, 50)
        
        assert len(result) == 1
        assert "summary_text" in result[0]
        assert len(result[0]["summary_text"]) <= 100
    
    def test_get_info(self):
        model = DummyModel()
        info = model.get_info()
        assert info["type"] == "dummy"
        assert info["loaded"] is False
        
        model.load("test")
        info = model.get_info()
        assert info["loaded"] is True
        assert info["model"] == "test"