import pytest
from unittest.mock import Mock, patch
from app.services.models.huggingface import HuggingFaceModel


class TestHuggingFaceModel:
    @patch("app.services.models.huggingface.pipeline")
    def test_load_success(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipeline.return_value = mock_pipe
        
        model = HuggingFaceModel()
        model.load("test-model")
        
        assert model._pipeline == mock_pipe
        assert model._model_name == "test-model"
        assert model.get_info()["type"] == "huggingface"
        mock_pipeline.assert_called_once_with("summarization", model="test-model")
    
    @patch("app.services.models.huggingface.pipeline")
    def test_load_failure(self, mock_pipeline):
        mock_pipeline.side_effect = Exception("Load failed")
        
        model = HuggingFaceModel()
        with pytest.raises(Exception, match="Load failed"):
            model.load("test-model")
    
    @patch("app.services.models.huggingface.pipeline")
    def test_summarize_success(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = [{"summary_text": "Summary"}]
        mock_pipeline.return_value = mock_pipe
        
        model = HuggingFaceModel()
        model.load("test-model")
        result = model.summarize("Long text", 100, 50)
        
        assert result == [{"summary_text": "Summary"}]
        mock_pipe.assert_called_once_with("Long text", max_length=100, min_length=50)
    
    def test_summarize_not_loaded(self):
        model = HuggingFaceModel()
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.summarize("text", 100, 50)