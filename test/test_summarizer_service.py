import pytest
from unittest.mock import Mock, patch
from app.services.summarizer import (
    SummarizerService, SummaryStyle, SummaryOption,
    SummaryResult, STYLE_PROMPTS, LENGTH_PARAMS
)
from app.utils.error_handler import InternalServerError


class TestSummarizerService:
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.summarize.return_value = [{"summary_text": "Test summary"}]
        return model
    
    def test_init_with_model(self, mock_model):
        service = SummarizerService(model=mock_model)
        assert service._model == mock_model
    
    @patch("app.services.summarizer.create_model")
    @patch("app.services.summarizer.get_settings")
    def test_init_without_model(self, mock_settings, mock_create):
        mock_settings.return_value.EMBEDDING_MODEL_TYPE = "dummy"
        mock_settings.return_value.EMBEDDING_MODEL_PATH = "/path"
        mock_settings.return_value.EMBEDDING_MODEL_PARAMS = {"param": "value"}
        
        mock_model = Mock()
        mock_create.return_value = mock_model
        
        service = SummarizerService()
        assert service._model == mock_model
        mock_create.assert_called_once_with(
            model_type="dummy",
            model_path="/path",
            param="value"
        )
    
    @pytest.mark.asyncio
    async def test_summarize(self, mock_model):
        service = SummarizerService(model=mock_model)
        result = await service.summarize(
            "Test text",
            "en",
            SummaryStyle.GENERAL,
            SummaryOption.MEDIUM
        )
        
        assert result == ("Test summary", "en", STYLE_PROMPTS[SummaryStyle.GENERAL])
        mock_model.summarize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_summarize_with_meta(self, mock_model):
        service = SummarizerService(model=mock_model)
        result = await service.summarize_with_meta(
            "Test text",
            "en",
            SummaryStyle.EMOTIONAL,
            SummaryOption.SHORT
        )
        
        assert isinstance(result, SummaryResult)
        assert result.text == "Test summary"
        assert result.language == "en"
        assert result.style_prompt == STYLE_PROMPTS[SummaryStyle.EMOTIONAL]
    
    def test_summarize_sync_all_styles(self, mock_model):
        service = SummarizerService(model=mock_model)
        
        for style in SummaryStyle:
            result = service._summarize_sync("text", "en", style, SummaryOption.MEDIUM)
            assert result[0] == "Test summary"
            assert result[2] == STYLE_PROMPTS[style]
    
    def test_summarize_sync_all_options(self, mock_model):
        service = SummarizerService(model=mock_model)
        
        for option in SummaryOption:
            service._summarize_sync("text", "en", SummaryStyle.GENERAL, option)
            params = LENGTH_PARAMS[option]
            mock_model.summarize.assert_called_with(
                f"{STYLE_PROMPTS[SummaryStyle.GENERAL]} text",
                max_length=params["max_length"],
                min_length=params["min_length"]
            )
    
    def test_summarize_sync_error(self, mock_model):
        mock_model.summarize.side_effect = Exception("Model error")
        service = SummarizerService(model=mock_model)
        
        with pytest.raises(InternalServerError, match="Failed to summarize text"):
            service._summarize_sync("text", "en", SummaryStyle.GENERAL, SummaryOption.MEDIUM)