import pytest
from unittest.mock import Mock, patch
from app.services.model_factory import create_model, register_model, _MODEL_REGISTRY
from app.services.base_model import BaseEmbeddingModel


class MockModel(BaseEmbeddingModel):
    def __init__(self):
        self.loaded = False
    
    def load(self, model_path, **kwargs):
        self.loaded = True
        self.path = model_path
    
    def summarize(self, text, max_length, min_length, **kwargs):
        return [{"summary_text": "mock"}]
    
    def get_info(self):
        return {"type": "mock"}


class TestModelFactory:
    def test_register_model(self):
        register_model("test_mock", MockModel)
        assert "test_mock" in _MODEL_REGISTRY
        assert _MODEL_REGISTRY["test_mock"] == MockModel
    
    def test_create_registered_model(self):
        register_model("test_mock", MockModel)
        model = create_model("test_mock", "/test/path")
        assert isinstance(model, MockModel)
        assert model.loaded
        assert model.path == "/test/path"
    
    def test_create_builtin_models(self):
        model = create_model("dummy", "/dummy/path")
        assert model.get_info()["type"] == "dummy"
        
        with patch("app.services.models.huggingface.pipeline"):
            model = create_model("huggingface", "facebook/bart")
            assert model.get_info()["type"] == "huggingface"
    
    @patch("importlib.import_module")
    def test_dynamic_import(self, mock_import):
        mock_module = Mock()
        mock_module.CustomModel = MockModel
        mock_import.return_value = mock_module
        
        model = create_model("custom.module.CustomModel", "/path")
        assert isinstance(model, MockModel)
        mock_import.assert_called_once_with("custom.module")
    
    def test_unknown_model_type(self):
        with pytest.raises(ValueError, match="Unknown model type"):
            create_model("nonexistent", "/path")